"""The console's fixed paths, names and limits: the AI launcher, the splash, the control socket, production."""

from __future__ import annotations

import os
import re
import string

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
CONTROL_ONLY = (
    re.compile(rb"\x1B\][^\x07\x1B]*(?:\x07|\x1B\\)"),
    re.compile(rb"\x1B[P_^X][^\x1B]*\x1B\\"),
    re.compile(rb"\x1B\[[0-?]*[ -/]*[@-~]"),
    re.compile(rb"\x1B[@-Z\\-_]"),
)
#: The bytes of terminal escape sequences, read by `dooservice_terminal`.
ESC = 0x1B
BEL = 0x07
CSI_OPEN = ord("[")
OSC_OPEN = ord("]")
STRING_TERMINATOR = ord("\\")
HYPERLINK = b"8;"
SECURE_URL = b"https://"
#: The providers an unattended build runs on, and what it is started with.
BUILD_PROVIDERS = ("anthropic", "openai", "openai_compatible")
BUILD_MODULE_CHARACTERS = frozenset(string.ascii_lowercase + string.digits + "_")
BUILD_REQUIRED = (
    "DOOSERVICE_BUILD_PROVIDER",
    "DOOSERVICE_BUILD_MODEL",
    "DOOSERVICE_BUILD_KEY",
    "DOOSERVICE_BUILD_MODULE",
    "DOOSERVICE_BUILD_DIR",
    "DOOSERVICE_BUILD_PROMPT",
)
BUILD_KEPT_OUT = ("DOOSERVICE_BUILD_KEY", "DOOSERVICE_BUILD_PROMPT")
#: What a build may read besides the repository, and how opencode reaches a service compatible with OpenAI.
BUILD_ODOO_SOURCE = "/usr/lib/python3/dist-packages/odoo/"
BUILD_PLATFORM_ADDONS = "/opt/dooservice/addons/"
COMPATIBLE_PACKAGE = "@ai-sdk/openai-compatible"
COMPATIBLE_PROVIDER = "dooservice"
