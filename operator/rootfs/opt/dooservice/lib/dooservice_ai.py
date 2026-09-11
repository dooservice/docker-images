"""What both AI launchers share: whether a session may start, and the terminal it runs in.

Three guards before anything starts. The environment has to be a development one: an
agent that edits code and runs `odoo-bin -u` without asking belongs on a database that is
not a customer's. Only one AI session per container, so two agents never edit the same
files at once. And the platform has to agree: the launcher asks the agent to hold this
environment's deploys, and waits for the answer — a pull that resets the addons under a
working agent would throw its work away.

Then the agent runs inside a pseudo-terminal of its own, which rewrites two things on
the way through. A login URL the agent prints is made clickable and announced to the
browser with an OSC 9 sequence, so signing in is one click instead of copying a URL the
terminal has broken across lines. And Ctrl+Z never reaches the agent: a suspended agent
is a session that holds the environment without anyone seeing it.
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

    @staticmethod
    def announce_login(data):
        """Make a login URL clickable and tell the browser about it.

        The terminal wraps a long URL across lines and pads it with escape codes, so it is
        stitched back together from the first known prefix up to the first word that is
        plainly not part of it.
        """
        target = next((url for url in LOGIN_URLS if url in data), None)
        if target is None:
            return data
        tail = ANSI_ESCAPE.sub(b"", data[data.find(target):])
        pieces = []
        for token in re.sub(rb"\s+", b" ", tail).split(b" "):
            if not token.strip():
                continue
            if token.lower() in URL_TERMINATORS:
                break
            pieces.append(token.strip())
        url = b"".join(pieces)
        if not url.startswith(b"https://"):
            return data
        announcement = json.dumps({"action": "open_url", "url": url.decode("utf-8", errors="ignore")})
        clickable = b"\x1b]8;;" + url + b"\x07" + target + b"\x1b]8;;\x07"
        data = data.replace(target, clickable, 1)
        return data + b"\x1b]9;" + base64.b64encode(announcement.encode()) + b"\x07"
