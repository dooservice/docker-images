"""The person's language, as the platform passes it, reduced to the code the console speaks."""

from __future__ import annotations

import os

from .constants import LANGUAGE_NAMES, LANGUAGE_VARIABLE


class Language:
    """`es`, `pt-BR` or `en_US` from the platform, read as `es`, `pt` or `en`."""

    def __init__(self, value: str | None = None) -> None:
        raw = os.environ.get(LANGUAGE_VARIABLE, "") if value is None else value
        self.code = raw.replace("_", "-").partition("-")[0].lower()

    @property
    def name(self) -> str | None:
        """The language's English name, when the console speaks it."""
        return LANGUAGE_NAMES.get(self.code)

    def pick(self, table: dict[str, str], default: str) -> str:
        """This language's entry of a translation table, or the default."""
        return table.get(self.code, default)

    def rule(self) -> str:
        """The one sentence that keeps the agent in the person's language all session.

        Said outright rather than left to the agent: it starts in the language it is
        written to, and drifts to English after a few screens of logs and source code.
        """
        if self.name is None:
            return ("Always reply to the user in the language they write in, for the whole session, even when "
                    "files, logs, code or command output are in another language.")
        return (f"Always reply to the user in {self.name}, for the whole session, even when files, logs, code or "
                "command output are in another language. Keep code, commands and identifiers as they are.")
