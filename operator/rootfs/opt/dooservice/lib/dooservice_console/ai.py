"""What both AI launchers share: whether a session may start, and the terminal it runs in.

Three guards before anything starts. The environment has to be development, or
production when the platform opened the console with the AI allowed there: on production
it reads, and changes data only through Odoo, after the person said yes to each change.
Only one AI session per container, so two agents never work over each other.
And the platform has to agree: the launcher asks the agent for the environment's one AI
slot, and waits for the answer.

There is one kind of session. The agent configures Odoo through its shell and writes code
only once the person agrees, in the project's repository; a project without one is
configured only, with the file-editing tools switched off. Either way `psql` is read
only for the agent: data changes go through the ORM, where Odoo's own checks run.

The instructions are one file. Claude Code is given it as `~/.claude/CLAUDE.md`, one line
importing it, which it always loads; opencode reads it from its configuration. Every
skill is linked where each tool looks for them.

Then the agent runs inside a pseudo-terminal of its own, which watches two things on the
way through. A login URL the agent prints is announced to the browser with an OSC 9
sequence, so signing in is one click instead of copying a URL the terminal has broken
across lines; what the agent prints is passed on untouched, its own links included. And
Ctrl+Z never reaches the agent: a suspended agent is a session that holds the
environment without anyone seeing it.
"""

import base64
import contextlib
import fcntl
import json
import os
import pty
import select
import struct
import sys
import termios
import tty

from .constants import (
    ANNOUNCE_CLOSE,
    ANNOUNCE_OPEN,
    CTRL_Z,
    DEVELOPMENT,
    FRAME_SECONDS,
    INSTRUCTIONS,
    KEYS_BYTES,
    LOCK_PATH,
    LOGIN_URLS,
    NO_REPOSITORY,
    NUL,
    PRODUCTION,
    READ_BYTES,
    REPOSITORY,
    SEEN_BYTES,
    SESSION_MARK,
    SETTINGS_FILES,
    SKILL_GROUPS,
    SKILLS_DIR,
    STAGE_VARIABLE,
    URL_TERMINATORS,
)
from .control import ControlClient, ControlError
from .splash import Splash
from .terminal import TerminalText


class Workspace:
    """Where the agent works, the file that tells it how, and the skills it has: the
    repository when the project has one, its home otherwise, where it cannot edit files.
    On production it never has the repository, and asks before each thing that writes."""

    def __init__(self):
        self.has_repository = os.path.isdir(os.path.join(REPOSITORY, ".git"))
        self.project = REPOSITORY if self.has_repository else os.path.expanduser("~")
        self.instructions = INSTRUCTIONS
        if os.environ.get(STAGE_VARIABLE) == PRODUCTION:
            case = PRODUCTION
        else:
            case = DEVELOPMENT if self.has_repository else NO_REPOSITORY
        self.claude_settings = SETTINGS_FILES["claude"][case]
        self.opencode_config = SETTINGS_FILES["opencode"][case]

    def describe(self):
        return "with the project's repository" if self.has_repository else "without a repository, to configure only"

    def link_skills(self, into):
        """Every skill, linked into the directory a tool reads them from."""
        os.makedirs(into, exist_ok=True)
        for group in SKILL_GROUPS:
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


class AiSession:
    """One AI tool's run: the guards before it, the terminal it runs in, the slot it holds."""

    def __init__(self, tool):
        self.tool = tool
        self.lock = None
        self.platform = ControlClient()
        self.held = False
        self.seen = b""
        self.announced = set()
        self.workspace = Workspace()
        os.environ[SESSION_MARK] = "1"

    def begin(self):
        """Every guard, in order. Exits with a sentence a person can act on."""
        if os.environ.get(STAGE_VARIABLE) not in (DEVELOPMENT, PRODUCTION):
            self.refuse("AI sessions run on development, and on production when the organization allows it.")
        self.lock = open(LOCK_PATH, "w")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.refuse("Another AI session is already running in this console. Close it before starting another.")
        if "--version" in sys.argv or "--help" in sys.argv:
            return
        try:
            self.platform.settle("ai_begin", {"tool": self.tool})
        except ControlError as error:
            self.refuse(str(error))
        except OSError as error:
            self.refuse(f"The platform did not answer ({error}). Try again in a moment.")
        self.held = True

    def end(self):
        """Give the AI slot back, once."""
        if self.held:
            with contextlib.suppress(ControlError, OSError):
                self.platform.settle("ai_end", {"tool": self.tool})
            self.held = False

    def refuse(self, message):
        """Stop before anything starts, with a sentence a person can act on."""
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
            child, master = pty.fork()
            if child == 0:
                os.execv(command[0], command)
            self.copy_window_size(master)
            splash.start()
            self.copy(master, splash)
            os.waitpid(child, 0)
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
                ready = select.select(sources, [], [], FRAME_SECONDS if splash.active else None)[0]
                if not ready:
                    if splash.finished():
                        self.reveal(splash, stdout)
                    else:
                        splash.draw()
                    continue
                if master in ready:
                    self.copy_window_size(master)
                    try:
                        data = os.read(master, READ_BYTES)
                    except OSError:
                        data = b""
                    if not data:
                        sources.remove(master)
                        self.reveal(splash, stdout)
                        continue
                    data = self.announce_login(data)
                    if splash.active and (splash.held or TerminalText.readable(data)):
                        splash.held.append(data)
                        if splash.finished():
                            self.reveal(splash, stdout)
                        continue
                    os.write(stdout, data)
                if stdin in ready:
                    data = os.read(stdin, KEYS_BYTES)
                    if not data:
                        sources.remove(stdin)
                        continue
                    os.write(master, data.replace(CTRL_Z, NUL))
        finally:
            if saved is not None:
                termios.tcsetattr(stdin, termios.TCSAFLUSH, saved)

    @staticmethod
    def copy_window_size(descriptor):
        """The person's terminal size, given to the agent's."""
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
        login_url = self.linked_login() or self.printed_login()
        if login_url is None or login_url in self.announced:
            return data
        self.announced.add(login_url)
        announcement = json.dumps({"action": "open_url", "url": login_url.decode("utf-8", errors="ignore")})
        return data + ANNOUNCE_OPEN + base64.b64encode(announcement.encode()) + ANNOUNCE_CLOSE

    def linked_login(self):
        """The last login URL printed as a terminal link."""
        links = TerminalText.links(self.seen)
        return next((link for link in reversed(links) if link.startswith(LOGIN_URLS)), None)

    def printed_login(self):
        """The last login URL printed as plain text, once its end has arrived."""
        text = TerminalText.plain(self.seen)
        start = max(text.rfind(prefix) for prefix in LOGIN_URLS)
        if start < 0:
            return None
        pieces = []
        for token in text[start:].split():
            if not token:
                continue
            if token.lower() in URL_TERMINATORS:
                login_url = b"".join(pieces)
                return login_url if login_url.startswith(LOGIN_URLS) else None
            pieces.append(token)
        return None
