"""A card made into the page the browser sees."""

from html import escape
from pathlib import Path
from string import Template

from .card import Card
from .cases import WORDING, Case
from .constants import (
    ACTIVE_POLL_MILLISECONDS,
    FINAL_POLL_MILLISECONDS,
    GLOBAL_SUPPORT,
    PANEL_URL,
    PERU_SUPPORT,
    SITE_URL,
)

CHOICES = (
    (" primary", SITE_URL, "Discover Dooservice", "If you do not know why you landed here"),
    ("", PANEL_URL, "My projects", "Check the list of your environments"),
    ("", f"mailto:{GLOBAL_SUPPORT}", "Get help", "If you want to recover a deleted environment"),
)

HERE = Path(__file__).parent


class Page:
    def __init__(self) -> None:
        self.template = Template((HERE / "page.html").read_text())
        self.logo = (HERE / "logo.svg").read_text().strip()

    def render(self, card: Card, host: str = "") -> str:
        wording = WORDING[card.case]
        missing = card.case == Case.UNKNOWN and bool(host)
        return self.template.substitute(
            logo=self.logo,
            label=escape(wording.label),
            title=escape(wording.title),
            heading=f"<mark>{escape(host)}</mark> does not exist (anymore?)" if missing else escape(wording.title),
            text=escape(wording.text),
            progress=self.progress(card) if card.progress is not None else self.dots(wording.final),
            actions=self.choices() if card.case == Case.UNKNOWN else self.actions(),
            every=FINAL_POLL_MILLISECONDS if wording.final else ACTIVE_POLL_MILLISECONDS,
            global_support=GLOBAL_SUPPORT,
            peru_support=PERU_SUPPORT,
            site_url=SITE_URL,
        )

    @staticmethod
    def progress(card: Card) -> str:
        return (
            f'<div class="meter" role="progressbar" aria-valuenow="{card.progress}" aria-valuemin="0" '
            f'aria-valuemax="100"><span style="width:{card.progress}%"></span></div>'
            f'<div class="step"><span>{escape(card.step)}</span><span>{card.progress}%</span></div>'
        )

    @staticmethod
    def dots(final: bool) -> str:
        return "" if final else '<div class="dots" aria-hidden="true"><i></i><i></i><i></i></div>'

    @staticmethod
    def actions() -> str:
        return (
            f'<div class="actions"><a class="btn primary" href="{PANEL_URL}">Open Dooservice</a>'
            f'<a class="btn" href="{SITE_URL}">Visit dooservice.sh</a></div>'
        )

    @staticmethod
    def choices() -> str:
        return '<div class="choices">' + "".join(
            f'<div><a class="btn{kind}" href="{url}">{label}</a><small>{caption}</small></div>'
            for kind, url, label, caption in CHOICES
        ) + "</div>"
