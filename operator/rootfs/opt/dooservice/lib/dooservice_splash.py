"""The dooservice logo, drawn while an AI tool boots.

opencode takes several seconds before it draws anything, and a black terminal looks like
a broken one. This fills the wait: the logo with a light sweeping across it, a spinner
and what is starting, in the person's language.

Frames travel to the browser like any terminal output, so they are kept small: a colour
is sent only where it changes.

It plays for at least `MINIMUM_SECONDS`, whichever tool it is: Claude Code is ready in a
second and opencode takes several, and both should open the same way rather than one
flashing past. What a tool draws before then is held and shown when the animation ends.

It is a frame renderer, not a loop of its own. The session's copy loop calls `draw` when
it has nothing else to do, so frames and the tool's own output never interleave, and it
ends the animation once the tool has something to show and the minimum has passed.
"""

import os
import re
import sys
import time

from dooservice_constants import (
    BAR_WIDTH,
    CONTROL_ONLY,
    GRAY,
    LOGO,
    MINIMUM_SECONDS,
    RESET,
    SPINNER,
    STARTING,
    TEAL,
    WHITE,
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
        self.started_at = 0.0
        self.held = []

    def start(self):
        self.active = True
        self.started_at = time.monotonic()
        self.write("\033[?25l\033[2J")
        self.draw()

    def finished(self):
        """The tool has something to show, and the animation has had its full time."""
        return self.active and bool(self.held) and time.monotonic() - self.started_at >= MINIMUM_SECONDS

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
