"""The person's language, as the platform passes it, reduced to the code the console speaks."""

from __future__ import annotations

import json
import os
from functools import cached_property
from pathlib import Path

from .constants import CONSOLE_LOCALE, DEFAULT_LANGUAGE, LANGUAGE_VARIABLE, LOCALES_DIR


class Catalog:
    """The console's texts in one language, from dooservice/locales' `<code>/console.json`.

    English fills any text the language lacks.
    Keys are dotted paths into the file: `starting`, `welcome.place`, `stages.production`.
    A language without a file reads entirely in English.
    """

    def __init__(self, code: str, directory: Path = LOCALES_DIR) -> None:
        self.directory = directory
        self.texts = self.load(DEFAULT_LANGUAGE) | self.load(code)

    def load(self, code: str) -> dict[str, str]:
        """One locale file's texts by dotted key; nothing for a language without a file or an odd code."""
        path = self.directory / code / CONSOLE_LOCALE
        if not code.isalpha() or not path.is_file():
            return {}
        return self.flatten(json.loads(path.read_text(encoding="utf-8")))

    @classmethod
    def flatten(cls, table: dict, prefix: str = "") -> dict[str, str]:
        """A JSON document's strings, keyed by their dotted path."""
        texts: dict[str, str] = {}
        for name, value in table.items():
            key = f"{prefix}{name}"
            if isinstance(value, dict):
                texts |= cls.flatten(value, f"{key}.")
            else:
                texts[key] = value
        return texts

    def text(self, key: str, default: str | None = None) -> str:
        """A key's text in this language, else in English, else the default; with no default, a KeyError."""
        if key in self.texts:
            return self.texts[key]
        if default is None:
            raise KeyError(key)
        return default


class Language:
    """`es`, `pt-BR` or `en_US` from the platform, read as `es`, `pt` or `en`."""

    def __init__(self, value: str | None = None) -> None:
        given = os.environ.get(LANGUAGE_VARIABLE, "") if value is None else value
        self.code = given.replace("_", "-").partition("-")[0].lower()

    @property
    def name(self) -> str | None:
        """The language's English name, when the platform offers it (dooservice/locales' `languages.json`)."""
        listed = LOCALES_DIR / "languages.json"
        if not listed.is_file():
            return None
        names = {entry["code"]: entry["name"] for entry in json.loads(listed.read_text(encoding="utf-8"))}
        return names.get(self.code)

    @cached_property
    def catalog(self) -> Catalog:
        """This language's texts, read once."""
        return Catalog(self.code)

    def text(self, key: str, default: str | None = None) -> str:
        """One of the console's texts in this language; see `Catalog.text`."""
        return self.catalog.text(key, default)

    def rule(self) -> str:
        """The one sentence that keeps the agent in the person's language all session.

        Said outright rather than left to the agent: it starts in the language it is
        written to, and drifts to English after a few screens of logs and source code.
        """
        if self.name is None:
            return (
                "Always reply to the user in the language they write in, for the whole session, even when "
                "files, logs, code or command output are in another language."
            )
        return (
            f"Always reply to the user in {self.name}, for the whole session, even when files, logs, code or "
            "command output are in another language. Keep code, commands and identifiers as they are."
        )
