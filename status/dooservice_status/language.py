"""The visitor's language, from the browser's `Accept-Language`, and the page's texts in it."""

import json
from pathlib import Path

from .constants import DEFAULT_LANGUAGE, LOCALES_DIR, STATUS_LOCALE


class AcceptLanguage:
    """The base codes a browser asks for, best first: `es-PE,en;q=0.8,fr;q=0` reads es, en.

    Ranges keep the order they came in when their weights tie; a weight of 0, a weight that
    is not a number and `*` ask for nothing.
    """

    def __init__(self, header: str) -> None:
        ranges = [self.range(part) for part in header.split(",")]
        ranked = sorted((-weight, index, code) for index, (code, weight) in enumerate(ranges) if code and weight > 0)
        self.codes = [code for _, _, code in ranked]

    @staticmethod
    def range(part: str) -> tuple[str, float]:
        tag, _, parameters = part.partition(";")
        code = tag.strip().replace("_", "-").partition("-")[0].lower()
        weight = 1.0
        for parameter in parameters.split(";"):
            name, _, value = parameter.partition("=")
            if name.strip().lower() == "q":
                try:
                    weight = float(value.strip())
                except ValueError:
                    weight = 0.0
        return (code if code.isalpha() else "", weight)


class Catalog:
    """The page's texts in one language by dotted key (`cases.creating.title`), with English
    filling any text the language lacks."""

    def __init__(self, code: str, texts: dict[str, str]) -> None:
        self.code = code
        self.texts = texts

    def text(self, key: str) -> str:
        return self.texts[key]


class Catalogs:
    """Every language with a `status.json` in dooservice/locales, read once at start."""

    def __init__(self, directory: Path = LOCALES_DIR) -> None:
        self.directory = directory
        english = self.load(DEFAULT_LANGUAGE)
        self.catalogs = {
            path.parent.name: Catalog(path.parent.name, english | self.load(path.parent.name))
            for path in sorted(directory.glob(f"*/{STATUS_LOCALE}"))
            if path.parent.name.isalpha()
        }

    def load(self, code: str) -> dict[str, str]:
        return self.flatten(json.loads((self.directory / code / STATUS_LOCALE).read_text(encoding="utf-8")))

    @classmethod
    def flatten(cls, table: dict, prefix: str = "") -> dict[str, str]:
        texts: dict[str, str] = {}
        for name, value in table.items():
            if isinstance(value, dict):
                texts |= cls.flatten(value, f"{prefix}{name}.")
            else:
                texts[f"{prefix}{name}"] = value
        return texts

    def of(self, header: str) -> Catalog:
        """The first language the browser asks for that the page speaks, else English."""
        for code in AcceptLanguage(header).codes:
            if code in self.catalogs:
                return self.catalogs[code]
        return self.catalogs[DEFAULT_LANGUAGE]
