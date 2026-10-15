"""The card the agent wrote for an address, read without trusting the address or the file."""

from dataclasses import dataclass
import json
from pathlib import Path

from .cases import Case
from .constants import CARD_SUFFIX, CARDS_DIR, HOST_CHARACTERS, MAX_HOST_LENGTH


@dataclass(frozen=True)
class Card:
    case: Case
    step: str = ""
    progress: int | None = None


class Host:
    """The name the browser asked for, lowercased and without its port, or nothing when it
    could not be a file name of the cards directory."""

    @staticmethod
    def of(header: str) -> str:
        host = header.strip().lower().partition(":")[0].rstrip(".")
        if not host or len(host) > MAX_HOST_LENGTH or not set(host) <= HOST_CHARACTERS:
            return ""
        if host.startswith(".") or ".." in host:
            return ""
        return host


class Cards:
    def __init__(self, directory: Path = CARDS_DIR) -> None:
        self.directory = directory

    def of(self, host: str) -> Card:
        if not host:
            return Card(Case.UNKNOWN)
        try:
            data = json.loads((self.directory / f"{host}{CARD_SUFFIX}").read_text())
            case = Case(data["case"])
        except (OSError, ValueError, KeyError, TypeError):
            return Card(Case.UNKNOWN)
        progress = data.get("progress")
        step = data.get("step")
        return Card(
            case,
            step if isinstance(step, str) else "",
            min(max(progress, 0), 100) if isinstance(progress, int) else None,
        )
