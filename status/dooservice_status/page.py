"""A card made into the page the browser sees, in the visitor's language."""

from html import escape
from pathlib import Path
from string import Template

from .card import Card
from .cases import Case
from .constants import (
    ACTIVE_POLL_MILLISECONDS,
    CHOICES,
    FINAL_POLL_MILLISECONDS,
    HOST_BLANK,
    PANEL_URL,
    SITE_URL,
    SUPPORT,
)
from .language import Catalog, Catalogs

HERE = Path(__file__).parent


class Page:
    def __init__(self, catalogs: Catalogs | None = None) -> None:
        self.template = Template((HERE / "page.html").read_text())
        self.logo = (HERE / "logo.svg").read_text().strip()
        self.catalogs = catalogs or Catalogs()

    def render(self, card: Card, host: str = "", accept_language: str = "") -> str:
        catalog = self.catalogs.of(accept_language)
        key = f"cases.{card.case.value}"
        title = escape(catalog.text(f"{key}.title"))
        missing = card.case == Case.UNKNOWN and bool(host)
        return self.template.substitute(
            lang=catalog.code,
            logo=self.logo,
            label=escape(catalog.text(f"{key}.label")),
            title=title,
            heading=self.missing(catalog, host) if missing else title,
            text=escape(catalog.text(f"{key}.text")),
            progress=self.progress(card) if card.progress is not None else self.dots(card.case.final),
            actions=self.choices(catalog) if card.case == Case.UNKNOWN else self.actions(catalog),
            every=FINAL_POLL_MILLISECONDS if card.case.final else ACTIVE_POLL_MILLISECONDS,
            help=escape(catalog.text("help")),
            support=SUPPORT,
            site_url=SITE_URL,
        )

    @staticmethod
    def missing(catalog: Catalog, host: str) -> str:
        return escape(catalog.text("missing")).replace(HOST_BLANK, f"<mark>{escape(host)}</mark>")

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
    def actions(catalog: Catalog) -> str:
        return (
            f'<div class="actions"><a class="btn primary" href="{PANEL_URL}">{escape(catalog.text("actions.open"))}</a>'
            f'<a class="btn" href="{SITE_URL}">{escape(catalog.text("actions.visit"))}</a></div>'
        )

    @staticmethod
    def choices(catalog: Catalog) -> str:
        return (
            '<div class="choices">'
            + "".join(
                f'<div><a class="btn{kind}" href="{url}">{escape(catalog.text(f"choices.{key}.label"))}</a>'
                f"<small>{escape(catalog.text(f'choices.{key}.hint'))}</small></div>"
                for kind, url, key in CHOICES
            )
            + "</div>"
        )
