"""What both AI launchers share: whether a session may start, and the terminal it runs in.

Three guards before anything starts. The environment has to be a development one: an
agent that runs `odoo-bin -u` without asking belongs on a database that is not a
customer's. Only one AI session per container, so two agents never work over each other.
And the platform has to agree: the launcher asks the agent for the environment's one AI
slot, and waits for the answer.

The session runs in one of two modes, chosen when the console is opened. Development
needs a repository: the agent works on the environment's modules and publishes them as
pull requests. Configuration is always possible, and the only one without a repository:
the agent sets up Odoo through its shell — parameters, users, companies, standard modules
— with its file-editing tools switched off and the database read only from `psql`.

Each mode has its instructions and its skills. Claude Code is given the instructions as
`~/.claude/CLAUDE.md`, one line importing the mode's file, which it always loads; opencode
reads them from its configuration. The skills are linked where each tool looks for them.

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
import select
import struct
import sys
import termios
import tty

from dooservice_control import ControlClient, ControlError
from dooservice_splash import Splash, readable

LOCK_PATH = "/tmp/dooservice-ai.lock"
DEVELOPMENT = "development"
REPOSITORY = "/mnt/addons"
AI_DIR = "/opt/dooservice/ai"
SKILLS_DIR = f"{AI_DIR}/skills"
CHOSEN = "DOOSERVICE_AI_MODE_CHOSEN"


LANGUAGE_NAMES = {
    "es": "Spanish",
    "en": "English",
    "pt": "Portuguese",
    "fr": "French",
    "it": "Italian",
    "de": "German",
}


def language_rule():
    """The one sentence that keeps the agent in the person's language all session.

    Said outright rather than left to the agent: it starts in the language it is
    written to, and drifts to English after a few screens of logs and source code.
    """
    code = os.environ.get("DOOSERVICE_LANGUAGE", "")
    name = LANGUAGE_NAMES.get(re.split(r"[-_]", code)[0].lower()) if code else None
    if name is None:
        return ("Always reply to the user in the language they write in, for the whole session, even when "
                "files, logs, code or command output are in another language.")
    return (f"Always reply to the user in {name}, for the whole session, even when files, logs, code or "
            "command output are in another language. Keep code, commands and identifiers as they are.")


class Mode:
    """What the agent is there to do, the files that tell it how, and the skills it has."""

    def __init__(self, name, project, instructions, claude_settings, opencode_config, skills):
        self.name = name
        self.project = project
        self.instructions = instructions
        self.claude_settings = claude_settings
        self.opencode_config = opencode_config
        self.skills = skills

    @classmethod
    def current(cls):
        """Development when it was chosen and there is a repository; configuration otherwise."""
        has_repository = os.path.isdir(os.path.join(REPOSITORY, ".git"))
        if has_repository and os.environ.get(CHOSEN, "code") != "functional":
            return cls("development", REPOSITORY, f"{AI_DIR}/AGENTS.md",
                       f"{AI_DIR}/settings.json", f"{AI_DIR}/opencode.json", ("code", "dooservice"))
        return cls("configuration", os.path.expanduser("~"), f"{AI_DIR}/CONFIGURATION.md",
                   f"{AI_DIR}/settings-configuration.json", f"{AI_DIR}/opencode-configuration.json",
                   ("functional",))

    def link_skills(self, into):
        """This mode's skills, linked into the directory a tool reads them from."""
        os.makedirs(into, exist_ok=True)
        for group in self.skills:
            source = os.path.join(SKILLS_DIR, group)
            if not os.path.isdir(source):
                continue
            for name in sorted(os.listdir(source)):
                target = os.path.join(into, name)
                if not os.path.lexists(target):
                    os.symlink(os.path.join(source, name), target)

    def claude_memory(self, claude_dir):
        """The instructions, as the one file Claude Code always loads: a line importing them."""
        os.makedirs(claude_dir, exist_ok=True)
        with open(os.path.join(claude_dir, "CLAUDE.md"), "w") as memory:
            memory.write(f"@{self.instructions}\n")


CTRL_Z = b"\x1a"
FRAME_SECONDS = 0.1
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
        self.mode = Mode.current()
        os.environ["DOOSERVICE_AI_MODE"] = self.mode.name

    def begin(self):
        """Every guard, in order. Exits with a sentence a person can act on."""
        if os.environ.get("DOOSERVICE_STAGE") != DEVELOPMENT:
            self.refuse("AI sessions only run on development environments. Clone this one to development first.")
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

    def execute(self, command, tool_name):
        """Run the agent in a terminal of its own, with the logo drawn until it draws.

        The copy loop is written out rather than left to `pty.spawn`, which waits on the
        terminal with no timeout: the splash needs the idle moments to draw its frames,
        and drawing them from the same loop that copies the agent's output is what keeps
        the two from ever writing over each other.
        """
        splash = Splash(tool_name)
        try:
            pid, master = pty.fork()
            if pid == 0:
                os.execv(command[0], command)
            self.copy_window_size(master)
            splash.start()
            self.copy(master, splash)
            os.waitpid(pid, 0)
        except Exception as error:
            splash.stop()
            sys.stderr.write(f"Error launching the AI agent: {error}\n")
        finally:
            splash.stop()
            self.end()

    @staticmethod
    def reveal(splash, stdout):
        """End the animation and show what the agent drew while it was playing."""
        if not splash.active:
            return
        splash.stop()
        for data in splash.held:
            os.write(stdout, data)
        splash.held.clear()

    def copy(self, master, splash):
        """Keystrokes to the agent, its output to the screen, until it exits.

        While the animation plays, the agent's questions to the terminal go straight
        through — it waits for their answers — but what it draws is held until the
        animation has had its full time, so a fast tool and a slow one open alike.
        """
        stdin = sys.stdin.fileno()
        stdout = sys.stdout.fileno()
        saved = None
        try:
            saved = termios.tcgetattr(stdin)
            tty.setraw(stdin)
        except termios.error:
            saved = None
        sources = [master, stdin]
        try:
            while master in sources:
                ready, _, _ = select.select(sources, [], [], FRAME_SECONDS if splash.active else None)
                if not ready:
                    if splash.finished():
                        self.reveal(splash, stdout)
                    else:
                        splash.draw()
                    continue
                if master in ready:
                    self.copy_window_size(master)
                    try:
                        data = os.read(master, 65536)
                    except OSError:
                        data = b""
                    if not data:
                        sources.remove(master)
                        self.reveal(splash, stdout)
                        continue
                    data = self.announce_login(data)
                    if splash.active and (splash.held or readable(data)):
                        splash.held.append(data)
                        if splash.finished():
                            self.reveal(splash, stdout)
                        continue
                    os.write(stdout, data)
                if stdin in ready:
                    data = os.read(stdin, 1024)
                    if not data:
                        sources.remove(stdin)
                        continue
                    os.write(master, data.replace(CTRL_Z, b"\x00"))
        finally:
            if saved is not None:
                termios.tcsetattr(stdin, termios.TCSAFLUSH, saved)

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
