"""Where the agent leaves each address's card, and how this service answers."""

from pathlib import Path

#: Mounted read only: the agent writes `<host>.json` here and nothing else does.
CARDS_DIR = Path("/status")
CARD_SUFFIX = ".json"
HOST_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789.-")
MAX_HOST_LENGTH = 253

PORT = 8080
HEALTH_PATH = "/_dooservice/health"
#: Where the proxy sends a production Odoo that answered 500. Its card still says what
#: the environment is; while nothing else is happening to it, the page says it failed.
FAILED_PATH = "/_dooservice/status/500"

#: Cases that move on by themselves poll often; the rest, in case somebody starts it again.
ACTIVE_POLL_MILLISECONDS = 3000
FINAL_POLL_MILLISECONDS = 30000
RETRY_AFTER_SECONDS = "5"

#: Not 502 to 504: the proxy sends those back here, and a final case is final.
WAITING_STATUS = 503
FINAL_STATUS = 404

PANEL_URL = "https://app.dooservice.sh"
SITE_URL = "https://dooservice.sh"
SUPPORT = "support@dooservice.sh"

#: Every text the page shows, from dooservice/locales: `<code>/status.json`. Beside the
#: package both in the image (/app/locales) and in a checkout (the status/locales submodule).
LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
#: The page's own file inside each language's folder.
STATUS_LOCALE = "status.json"
#: The language a visitor gets when the browser asks for none the page speaks, and the one
#: every other language falls back to, text by text.
DEFAULT_LANGUAGE = "en"
#: The blank the heading of an address with no Odoo fills with that address.
HOST_BLANK = "{host}"
#: Cases nothing moves on from by itself: they poll slowly and answer FINAL_STATUS.
FINAL_CASES = frozenset({"stopped", "expired", "unknown"})
#: What the page of an address with no Odoo offers: the button's class, where it leads, and
#: the key of its label and hint under `choices` of `status.json`.
CHOICES = (
    (" primary", SITE_URL, "discover"),
    ("", PANEL_URL, "projects"),
    ("", f"mailto:{SUPPORT}", "help"),
)
