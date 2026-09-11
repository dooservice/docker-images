"""What both AI launchers share: whether a session may start, and the terminal it runs in.

Three guards before anything starts. The environment has to be a development one: an
agent that edits code and runs `odoo-bin -u` without asking belongs on a database that is
not a customer's. Only one AI session per container, so two agents never edit the same
files at once. And the platform has to agree: the launcher asks the agent to hold this
environment's deploys, and waits for the answer — a pull that resets the addons under a
working agent would throw its work away.

Then the agent runs inside a pseudo-terminal of its own, which watches two things on the
way through. A login URL the agent prints is announced to the browser with an OSC 9
sequence, so signing in is one click instead of copying a URL the terminal has broken
across lines; what the agent prints is passed on untouched, its own links included. And
Ctrl+Z never reaches the agent: a suspended agent is a session that holds the
environment without anyone seeing it.
"""

import base64
import fcntl
import json
import os
import pty
import re
import struct
import sys
import termios

from dooservice_control import ControlClient, ControlError

LOCK_PATH = "/tmp/dooservice-ai.lock"
DEVELOPMENT = "development"
CTRL_Z = b"\x1a"
ANSI_ESCAPE = re.compile(rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
OSC_SEQUENCE = re.compile(rb"\x1B\][^\x07\x1B]*(?:\x07|\x1B\\)")
OSC_LINK = re.compile(rb"\x1B\]8;[^;\x07\x1B]*;(https://[^\x07\x1B]+)(?:\x07|\x1B\\)")
SEEN_BYTES = 16 * 1024
LOGIN_URLS = (
    b"https://console.anthropic.com/oauth/authorize",
    b"https://claude.ai/oauth/authorize",
    b"https://platform.claude.com/oauth/authorize",
    b"https://claude.com/cai/oauth/authorize",
    b"https://auth.openai.com/oauth/authorize",
)
URL_TERMINATORS = {b"authorization", b"code", b"enter", b"submit", b"esc", b"paste", b"here"}


class AiSession:
    def __init__(self, tool):
        self.tool = tool
        self.lock = None
        self.platform = ControlClient()
        self.held = False
        self.seen = b""
        self.announced = set()

    def begin(self):
        """Every guard, in order. Exits with a sentence a person can act on."""
        if os.environ.get("DOOSERVICE_STAGE") != DEVELOPMENT:
            self.refuse("AI sessions only run on development environments. Clone this one to development first.")
        if not os.path.isdir("/mnt/extra-addons/.git"):
            self.refuse("This environment has no repository, so there is nowhere for the agent's work to be kept.")
        self.lock = open(LOCK_PATH, "w")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.refuse("Another AI session is already running in this console. Close it before starting another.")
        if "--version" in sys.argv or "--help" in sys.argv:
            return
        try:
            for _ in self.platform.ask("ai_begin", {"tool": self.tool}):
                pass
        except ControlError as error:
            self.refuse(str(error))
        except OSError as error:
            self.refuse(f"The platform did not answer ({error}). Try again in a moment.")
        self.held = True

    def end(self):
        if self.held:
            try:
                for _ in self.platform.ask("ai_end", {"tool": self.tool}):
                    pass
            except (ControlError, OSError):
                pass
            self.held = False

    def refuse(self, message):
        sys.stderr.write(f"\n  {message}\n\n")
        sys.exit(1)

    def execute(self, command):
        try:
            pty.spawn(command, self.read_agent, self.read_keyboard)
        except Exception as error:
            sys.stderr.write(f"Error launching the AI agent: {error}\n")
        finally:
            self.end()

    def read_agent(self, descriptor):
        self.copy_window_size(descriptor)
        data = os.read(descriptor, 2048)
        return self.announce_login(data)

    def read_keyboard(self, descriptor):
        return os.read(descriptor, 1024).replace(CTRL_Z, b"\x00")

    @staticmethod
    def copy_window_size(descriptor):
        try:
            size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
            fcntl.ioctl(descriptor, termios.TIOCSWINSZ, size)
        except OSError:
            pass

    def announce_login(self, data):
        """Tell the browser about a login URL, once, and pass the output on untouched.

        What arrives here is chunks of a terminal stream, so the last stretch of it is
        kept and searched whole. A tool that prints the URL as a terminal link (OSC 8)
        carries it there complete; that is preferred. Otherwise the URL is stitched back
        together from the plain text — the terminal wraps it across lines and pads it
        with escape codes — from the first known prefix up to the first word plainly not
        part of it, and only once that word has arrived, so a URL cut at a chunk boundary
        is never announced half written.
        """
        self.seen = (self.seen + data)[-SEEN_BYTES:]
        url = self.linked_login() or self.printed_login()
        if url is None or url in self.announced:
            return data
        self.announced.add(url)
        announcement = json.dumps({"action": "open_url", "url": url.decode("utf-8", errors="ignore")})
        return data + b"\x1b]9;" + base64.b64encode(announcement.encode()) + b"\x07"

    def linked_login(self):
        links = [match.group(1) for match in OSC_LINK.finditer(self.seen)]
        return next((link for link in reversed(links) if link.startswith(LOGIN_URLS)), None)

    def printed_login(self):
        text = ANSI_ESCAPE.sub(b"", OSC_SEQUENCE.sub(b"", self.seen))
        start = max(text.rfind(prefix) for prefix in LOGIN_URLS)
        if start < 0:
            return None
        pieces = []
        for token in re.sub(rb"\s+", b" ", text[start:]).split(b" "):
            if not token:
                continue
            if token.lower() in URL_TERMINATORS:
                url = b"".join(pieces)
                return url if url.startswith(LOGIN_URLS) else None
            pieces.append(token)
        return None
