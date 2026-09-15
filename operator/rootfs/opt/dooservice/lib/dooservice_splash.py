"""The dooservice logo, drawn while an AI tool boots.

opencode takes several seconds before it draws anything, and a black terminal looks like
a broken one. This fills the wait: the logo with a light sweeping across it, a spinner
and what is starting, in the person's language.

Frames travel to the browser like any terminal output, so they are kept small: a colour
is sent only where it changes.

It is a frame renderer, not a loop of its own. The session's copy loop calls `draw` when
it has nothing else to do, so frames and the tool's own output never interleave, and it
calls `stop` the moment the tool prints something a person can read.
"""

import os
import re
import sys

LOGO = (
    "     _                                   _",
    "  __| | ___   ___  ___  ___ _ ____   __(_) ___ ___",
    " / _` |/ _ \\ / _ \\/ __|/ _ \\ '__\\ \\ / /| |/ __/ _ \\",
    "| (_| | (_) | (_) \\__ \\  __/ |   \\ V / | | (_|  __/",
    " \\__,_|\\___/ \\___/|___/\\___|_|    \\_/  |_|\\___\\___|",
)
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
TEAL = (98, 184, 195)
WHITE = (255, 255, 255)
GRAY = "\033[38;2;110;118;129m"
RESET = "\033[0m"
BAR_WIDTH = 24
STARTING = {"es": "Iniciando", "pt": "Iniciando", "fr": "Démarrage de", "it": "Avvio di", "de": "Starte"}

CONTROL_ONLY = (
    re.compile(rb"\x1B\][^\x07\x1B]*(?:\x07|\x1B\\)"),
    re.compile(rb"\x1B[P_^X][^\x1B]*\x1B\\"),
    re.compile(rb"\x1B\[[0-?]*[ -/]*[@-~]"),
    re.compile(rb"\x1B[@-Z\\-_]"),
)


def readable(data):
    """Whether output carries text for a person, not only questions to the terminal."""
    for sequence in CONTROL_ONLY:
        data = sequence.sub(b"", data)
    return re.search(rb"[^\s\x00-\x1f]", data) is not None


def color(rgb):
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def blend(start, end, amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(start, end))


class Splash:
    def __init__(self, tool_name):
        code = re.split(r"[-_]", os.environ.get("DOOSERVICE_LANGUAGE", ""))[0].lower()
        self.title = f"{STARTING.get(code, 'Starting')} {tool_name}"
        environment = os.environ.get("DOOSERVICE_ENVIRONMENT", "")
        project = os.environ.get("DOOSERVICE_PROJECT", "")
        self.subtitle = " · ".join(part for part in ("dooservice", project, environment) if part)
        self.active = False
        self.frame = 0

    def start(self):
        self.active = True
        self.write("\033[?25l\033[2J")
        self.draw()

    def stop(self):
        if not self.active:
            return
        self.active = False
        self.write("\033[2J\033[H\033[?25h")

    def draw(self):
        if not self.active:
            return
        try:
            columns, rows = os.get_terminal_size(sys.stdout.fileno())
        except OSError:
            columns, rows = 80, 24
        width = max(len(line) for line in LOGO)
        top = max(1, (rows - len(LOGO) - 5) // 2)
        sweep = (self.frame * 1.5) % (width + 24) - 12
        out = ["\0337"]
        for index, line in enumerate(LOGO):
            left = max(1, (columns - width) // 2 + 1)
            out.append(f"\033[{top + index};{left}H")
            current = None
            for column, char in enumerate(line):
                shade = color(blend(TEAL, WHITE, round(max(0.0, 1 - abs(column - sweep) / 6), 1)))
                if char != " " and shade != current:
                    out.append(shade)
                    current = shade
                out.append(char)
        spinner = SPINNER[self.frame % len(SPINNER)]
        dots = "." * (self.frame // 4 % 4)
        title = f"{spinner}  {self.title}{dots:<3}"
        head = self.frame % (BAR_WIDTH * 2)
        head = head if head < BAR_WIDTH else BAR_WIDTH * 2 - head - 1
        bar = "".join(
            (color(blend(TEAL, WHITE, round(1 - abs(i - head) / 4, 1))) + "━") if abs(i - head) < 4
            else (color(TEAL) + "─" if abs(i - head) == 4 else "─")
            for i in range(BAR_WIDTH)
        )
        for offset, (text, visible, styled) in enumerate((
            (title, len(title), color(TEAL) + title),
            (bar, BAR_WIDTH, bar),
            (self.subtitle, len(self.subtitle), GRAY + self.subtitle),
        )):
            left = max(1, (columns - visible) // 2 + 1)
            out.append(f"\033[{top + len(LOGO) + 2 + offset};{left}H\033[2K\033[{left}G{styled}")
        out.append(RESET + "\0338")
        self.write("".join(out))
        self.frame += 1

    @staticmethod
    def write(text):
        try:
            os.write(sys.stdout.fileno(), text.encode())
        except OSError:
            pass
