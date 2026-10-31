"""The banner a console's shell opens with, in the person's language.

Where the person is (project, stage, environment, Odoo, server), the commands worth
knowing, and what this session allows. How long the session lasts is the platform's to
say: the numbers come from what it passes, and without them the banner says it without
a number rather than guess one.

Run by /etc/profile.d/dooservice.sh as `python3 -m dooservice_console.welcome`.
"""

from __future__ import annotations

import os
import sys

from .constants import (
    ENVIRONMENT_VARIABLE,
    HUSHLOGIN,
    IDLE_SECONDS_VARIABLE,
    LANGUAGE_VARIABLE,
    LOGO,
    MAX_SECONDS_VARIABLE,
    ODOO_VERSION_VARIABLE,
    PRODUCTION,
    PROJECT_VARIABLE,
    REPOSITORY,
    RESET,
    SERVER_VARIABLE,
    STAGE_VARIABLE,
    WELCOME_COLOURS,
    WELCOME_COMMANDS,
    WELCOME_DEFAULT,
    WELCOME_TEXTS,
)
from .language import Language


class Welcome:
    """The banner's lines, from the environment the platform gave this console."""

    def __init__(self, environ=None):
        self.environ = os.environ if environ is None else environ
        code = Language(self.environ.get(LANGUAGE_VARIABLE, "")).code
        self.texts = WELCOME_TEXTS.get(code, WELCOME_TEXTS[WELCOME_DEFAULT])
        self.stage = self.environ.get(STAGE_VARIABLE, "")

    def show(self):
        """Print the banner, to a terminal only and unless the person asked for silence."""
        if not sys.stdout.isatty() or os.path.exists(os.path.expanduser(HUSHLOGIN)):
            return
        print("\n".join(self.lines()) + "\n")

    def lines(self):
        teal, white, gray, alarm = (WELCOME_COLOURS[name] for name in ("teal", "white", "gray", "red"))
        stage_colour = alarm if self.stage == PRODUCTION else teal
        stage = self.texts.get(self.stage, self.stage)
        lines = [teal + "\n".join(LOGO) + RESET, ""]
        lines.append(
            self.texts["place"].format(
                project=f"{white}{self.environ.get(PROJECT_VARIABLE, '')}{RESET}",
                stage=f"{stage_colour}{stage}{RESET}",
                environment=f"{white}{self.environ.get(ENVIRONMENT_VARIABLE, '')}{RESET}",
            )
        )
        lines.append(
            self.texts["odoo"].format(
                odoo=f"{white}Odoo {self.environ.get(ODOO_VERSION_VARIABLE, '')}{RESET}",
                server=f"{white}{self.environ.get(SERVER_VARIABLE, '')}{RESET}",
            )
        )
        lines += ["", f"{white}{self.texts['commands']}{RESET}", ""]
        commands = [(name.format(modules=self.texts["modules"]), self.texts[text]) for name, text in WELCOME_COMMANDS]
        width = max(len(name) for name, description in commands) + 4
        lines += [f"  {white}${RESET} {teal}{name.ljust(width)}{RESET}{description}" for name, description in commands]
        lines.append("")
        if not os.path.isdir(os.path.join(REPOSITORY, ".git")):
            lines.append(f"{gray}{self.texts['no_repository']}{RESET}")
        if self.stage == PRODUCTION:
            lines.append(f"{alarm}{self.texts['production_data']}{RESET}")
            lines.append(f"{alarm}{self.texts['production_deploy']}{RESET}")
        lines.append(f"{gray}{self.duration()}{RESET}")
        return lines

    def duration(self):
        """How long the session lasts, with the platform's numbers when it passed them."""
        idle = self.minutes(IDLE_SECONDS_VARIABLE)
        sentences = [self.texts["idle"].format(minutes=idle) if idle else self.texts["idle_unknown"]]
        limit = self.minutes(MAX_SECONDS_VARIABLE)
        if limit:
            sentences.append(self.texts["limit"].format(minutes=limit))
        elif self.stage == PRODUCTION:
            sentences.append(self.texts["limit_unknown"])
        return " ".join(sentences)

    def minutes(self, variable):
        """A number of seconds the platform passed, in whole minutes; None when it passed none."""
        try:
            seconds = int(self.environ.get(variable, ""))
        except ValueError:
            return None
        return max(1, round(seconds / 60)) if seconds > 0 else None


if __name__ == "__main__":
    Welcome().show()
