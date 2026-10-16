"""The console's fixed paths, names and limits: the AI launcher, the splash, the control socket, production."""

from __future__ import annotations

import os

LOCK_PATH = "/tmp/dooservice-ai.lock"
DEVELOPMENT = "development"
PRODUCTION = "production"
REPOSITORY = "/mnt/addons"
AI_DIR = "/opt/dooservice/ai"
SKILLS_DIR = f"{AI_DIR}/skills"
SESSION_MARK = "DOOSERVICE_AI_SESSION"
LANGUAGE_NAMES = {
    "es": "Spanish",
    "en": "English",
    "pt": "Portuguese",
    "fr": "French",
    "it": "Italian",
    "de": "German",
}
CTRL_Z = b"\x1a"
FRAME_SECONDS = 0.1
SEEN_BYTES = 16 * 1024
LOGIN_URLS = (
    b"https://console.anthropic.com/oauth/authorize",
    b"https://claude.ai/oauth/authorize",
    b"https://platform.claude.com/oauth/authorize",
    b"https://claude.com/cai/oauth/authorize",
    b"https://auth.openai.com/oauth/authorize",
)
URL_TERMINATORS = {b"authorization", b"code", b"enter", b"submit", b"esc", b"paste", b"here"}

SOCKET_PATH = os.environ.get("DOOSERVICE_CONTROL_SOCKET", "/run/dooservice/control.sock")
TIMEOUT_SECONDS = 600

CONTROL_DIR = os.path.dirname(os.environ.get("DOOSERVICE_CONTROL_SOCKET", "/run/dooservice/control.sock"))
CHANGES_UNTIL = os.path.join(CONTROL_DIR, "changes-until")
WRITE_CREDENTIALS = os.path.join(CONTROL_DIR, "write-credentials")
READ_ONLY = "-c default_transaction_read_only=on"

LOGO = (
    "     _                                   _",
    "  __| | ___   ___  ___  ___ _ ____   __(_) ___ ___",
    " / _` |/ _ \\ / _ \\/ __|/ _ \\ '__\\ \\ / /| |/ __/ _ \\",
    "| (_| | (_) | (_) \\__ \\  __/ |   \\ V / | | (_|  __/",
    " \\__,_|\\___/ \\___/|___/\\___|_|    \\_/  |_|\\___\\___|",
)
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
TEAL = (98, 184, 195)
WHITE = (255, 255, 255)
GRAY = "\033[38;2;110;118;129m"
RESET = "\033[0m"
BAR_WIDTH = 24
MINIMUM_SECONDS = 5
STARTING = {"es": "Iniciando", "pt": "Iniciando", "fr": "Démarrage de", "it": "Avvio di", "de": "Starte"}
#: The bytes of terminal escape sequences, read by `dooservice_terminal`.
ESC = 0x1B
BEL = 0x07
CSI_OPEN = ord("[")
OSC_OPEN = ord("]")
STRING_TERMINATOR = ord("\\")
#: DCS, SOS, PM and APC: strings a terminal answers or keeps, run up to the string terminator.
CONTROL_STRING_OPENS = frozenset(b"PX^_")
HYPERLINK = b"8;"
SECURE_URL = b"https://"
