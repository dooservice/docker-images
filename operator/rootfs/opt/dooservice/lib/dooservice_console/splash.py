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

import contextlib
import os
import sys
import time

from .constants import (
    BAR_WIDTH,
    DEFAULT_TERMINAL_SIZE,
    ENVIRONMENT_VARIABLE,
    GRAY,
    LOGO,
    MINIMUM_SECONDS,
    PROJECT_VARIABLE,
    RESET,
    SPINNER,
    TEAL,
    WHITE,
)
from .language import Language


class Shade:
    """A colour between two, as the terminal's escape for it."""

    @staticmethod
    def escape(colour):
        return f"\033[38;2;{colour[0]};{colour[1]};{colour[2]}m"

    @staticmethod
    def blend(start, finish, amount):
        return tuple(round(first + (second - first) * amount) for first, second in zip(start, finish))

    @classmethod
    def between(cls, amount):
        """Teal at 0, white at 1."""
        return cls.escape(cls.blend(TEAL, WHITE, amount))


class Splash:
    """The animation, drawn one frame at a time by the session's copy loop."""

    def __init__(self, tool_name):
        self.title = f"{Language().text('starting')} {tool_name}"
        environment = os.environ.get(ENVIRONMENT_VARIABLE, "")
        project = os.environ.get(PROJECT_VARIABLE, "")
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
            columns, rows = DEFAULT_TERMINAL_SIZE
        width = max(len(line) for line in LOGO)
        top_row = max(1, (rows - len(LOGO) - 5) // 2)
        sweep = (self.frame * 1.5) % (width + 24) - 12
        frame = ["\0337"]
        for index, line in enumerate(LOGO):
            left = max(1, (columns - width) // 2 + 1)
            frame.append(f"\033[{top_row + index};{left}H")
            current = None
            for column, char in enumerate(line):
                shade = Shade.between(round(max(0.0, 1 - abs(column - sweep) / 6), 1))
                if char != " " and shade != current:
                    frame.append(shade)
                    current = shade
                frame.append(char)
        spinner = SPINNER[self.frame % len(SPINNER)]
        dots = "." * (self.frame // 4 % 4)
        title = f"{spinner}  {self.title}{dots:<3}"
        for offset, (visible, styled) in enumerate(
            (
                (len(title), Shade.escape(TEAL) + title),
                (BAR_WIDTH, self.bar()),
                (len(self.subtitle), GRAY + self.subtitle),
            )
        ):
            left = max(1, (columns - visible) // 2 + 1)
            frame.append(f"\033[{top_row + len(LOGO) + 2 + offset};{left}H\033[2K\033[{left}G{styled}")
        frame.append(RESET + "\0338")
        self.write("".join(frame))
        self.frame += 1

    def bar(self):
        """The progress bar, with a light running back and forth along it."""
        head = self.frame % (BAR_WIDTH * 2)
        head = head if head < BAR_WIDTH else BAR_WIDTH * 2 - head - 1
        cells = []
        for cell in range(BAR_WIDTH):
            distance = abs(cell - head)
            if distance < 4:
                cells.append(Shade.between(round(1 - distance / 4, 1)) + "━")
            elif distance == 4:
                cells.append(Shade.escape(TEAL) + "─")
            else:
                cells.append("─")
        return "".join(cells)

    @staticmethod
    def write(text):
        with contextlib.suppress(OSError):
            os.write(sys.stdout.fileno(), text.encode())
