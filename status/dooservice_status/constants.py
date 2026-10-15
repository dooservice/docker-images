"""Where the agent leaves each address's card, and how this service answers."""

from pathlib import Path

#: Mounted read only: the agent writes `<host>.json` here and nothing else does.
CARDS_DIR = Path("/status")
CARD_SUFFIX = ".json"
HOST_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789.-")
MAX_HOST_LENGTH = 253

PORT = 8080
HEALTH_PATH = "/_dooservice/health"

#: Cases that move on by themselves poll often; the rest, in case somebody starts it again.
ACTIVE_POLL_MILLISECONDS = 3000
FINAL_POLL_MILLISECONDS = 30000
RETRY_AFTER_SECONDS = "5"

#: Not 502 to 504: the proxy sends those back here, and a final case is final.
WAITING_STATUS = 503
FINAL_STATUS = 404

PANEL_URL = "https://app.dooservice.sh"
SITE_URL = "https://dooservice.sh"
GLOBAL_SUPPORT = "support@dooservice.sh"
PERU_SUPPORT = "soporte@apiservicesac.com"
