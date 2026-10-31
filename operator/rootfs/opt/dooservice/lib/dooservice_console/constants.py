"""The console's fixed paths, names and limits: the launchers, the splash, the control socket, production."""

from __future__ import annotations

import os

#: The environment's stage, `development` or `production`, as the platform passes it.
STAGE_VARIABLE = "DOOSERVICE_STAGE"
#: The person's language code, as the platform passes it (`es`, `en`, `pt-BR`...).
LANGUAGE_VARIABLE = "DOOSERVICE_LANGUAGE"
#: The project's name, as the platform passes it.
PROJECT_VARIABLE = "DOOSERVICE_PROJECT"
#: The environment's name, as the platform passes it.
ENVIRONMENT_VARIABLE = "DOOSERVICE_ENVIRONMENT"
#: The person's own directory for this environment's conversations, mounted by the platform.
HISTORY_VARIABLE = "DOOSERVICE_AI_HISTORY"
#: Whether to pick up the last conversation: anything but `0` means yes.
RESUME_VARIABLE = "DOOSERVICE_AI_RESUME"
#: Where opencode keeps its sessions, when the platform mounts the person's history.
OPENCODE_DB_VARIABLE = "OPENCODE_DB"
#: The configuration file opencode reads instead of its default.
OPENCODE_CONFIG_VARIABLE = "OPENCODE_CONFIG"
#: Set by the AI launchers for everything the agent starts, so `psql` and git know it is the agent's.
SESSION_MARK = "DOOSERVICE_AI_SESSION"
#: The Odoo version of the image, set by its build.
ODOO_VERSION_VARIABLE = "ODOO_VERSION"
#: The server the environment runs on, as the platform passes it.
SERVER_VARIABLE = "DOOSERVICE_SERVER"
#: The environment's addons path, as the platform passes it.
ADDONS_PATH_VARIABLE = "ADDONS_PATH"
#: The path of the control socket, as the platform passes it.
CONTROL_SOCKET_VARIABLE = "DOOSERVICE_CONTROL_SOCKET"

#: The development stage.
DEVELOPMENT = "development"
#: The production stage.
PRODUCTION = "production"
#: The case of a development session without a repository: it configures only.
NO_REPOSITORY = "no-repository"

#: Held while an AI session runs, so a console never runs two.
LOCK_PATH = "/tmp/dooservice-ai.lock"
#: Where the launchers write what their setup commands print.
AI_LOG = "/tmp/dooservice-ai.log"
#: The project's repository, when it has one.
REPOSITORY = "/mnt/addons"
#: The environment's filestore and sessions, shared with the running server.
DATA_DIR = "/var/lib/odoo"
#: The settings, the instructions and the skills of the AI tools.
AI_DIR = "/opt/dooservice/ai"
#: The skills, one directory per group.
SKILLS_DIR = f"{AI_DIR}/skills"
#: The skill groups linked into each tool, in this order.
SKILL_GROUPS = ("code", "dooservice")
#: The instructions every AI tool is given.
INSTRUCTIONS = f"{AI_DIR}/AGENTS.md"
#: The MCP servers Claude Code is given.
MCP_CONFIG = f"{AI_DIR}/mcp.json"
#: Odoo and its standard modules, read only.
ODOO_SOURCE = "/usr/lib/python3/dist-packages/odoo"

#: Claude Code as Anthropic ships it.
CLAUDE_BINARY = "/opt/ai/claude"
#: opencode as its authors ship it.
OPENCODE_BINARY = "/opt/ai/opencode"
#: Claude Code's subcommands that are run as they are, without the environment's arguments.
CLAUDE_PASSTHROUGH = ("agents", "auth", "doctor", "install", "mcp", "plugin", "setup-token", "update", "upgrade")
#: opencode's subcommands that are run as they are, without the project or `--continue`.
OPENCODE_PASSTHROUGH = (
    "completion", "acp", "mcp", "attach", "run", "debug", "providers", "agent", "upgrade", "uninstall", "serve",
    "web", "models", "stats", "export", "import", "github", "pr", "session", "db", "auth",
)
#: The settings file of each tool, by the case it is for.
SETTINGS_FILES = {
    "claude": {
        DEVELOPMENT: f"{AI_DIR}/settings.json",
        NO_REPOSITORY: f"{AI_DIR}/settings-no-repository.json",
        PRODUCTION: f"{AI_DIR}/settings-production.json",
    },
    "opencode": {
        DEVELOPMENT: f"{AI_DIR}/opencode.json",
        NO_REPOSITORY: f"{AI_DIR}/opencode-no-repository.json",
        PRODUCTION: f"{AI_DIR}/opencode-production.json",
    },
}
#: What opencode's plugins need, installed once at build time and copied into each session.
PLUGINS_TEMPLATE = "/opt/dooservice/opencode-config"
#: The home the build uses to let opencode install its plugins.
PLUGINS_BUILD_HOME = "/tmp/opencode-template-home"
#: What opencode logs once its plugins are installed and it is ready.
PLUGINS_READY = b"all LSPs are disabled"
#: How long the build waits for opencode to install its plugins.
PLUGINS_TIMEOUT_SECONDS = 180

#: The `odoo` that Odoo's package installs.
REAL_ODOO = "/usr/bin/odoo"
#: The `psql` that PostgreSQL's client installs.
REAL_PSQL = "/usr/bin/psql"
#: The console's own `odoo-bin`, with the environment's database wired in.
ODOO_WRAPPER = "/usr/local/bin/odoo-bin"
#: The console's own `dooservice` command.
DOOSERVICE_COMMAND = "/usr/local/bin/dooservice"
#: Odoo commands that connect to the database and get its options.
DATABASE_COMMANDS = ("server", "shell")
#: The PostgreSQL port when the platform passes none.
DEFAULT_DATABASE_PORT = "5432"
#: The connections one Odoo process of the console may hold, unless asked otherwise.
DEFAULT_MAXCONN = "--db_maxconn=4"
#: The options that install or update modules.
MODULE_OPTIONS = ("-i", "-u", "--init", "--update")
#: The same options, written with their value after `=`.
MODULE_OPTION_PREFIXES = ("--init=", "--update=")

#: The PostgreSQL option that opens every transaction read only.
READ_ONLY = "-c default_transaction_read_only=on"
#: The control socket of this session.
SOCKET_PATH = os.environ.get(CONTROL_SOCKET_VARIABLE, "/run/dooservice/control.sock")
#: How long a request to the platform may take.
TIMEOUT_SECONDS = 600
#: The session's control directory, which this container can read and not write.
CONTROL_DIR = os.path.dirname(SOCKET_PATH)
#: Until when changes are allowed on production, written by the platform once the backup is ready.
CHANGES_UNTIL = os.path.join(CONTROL_DIR, "changes-until")
#: The environment's own database credentials on production, once the backup is ready.
WRITE_CREDENTIALS = os.path.join(CONTROL_DIR, "write-credentials")
#: The most bytes read from the control socket at once.
SOCKET_READ_BYTES = 65536
#: The exit code when the session has no connection to the platform.
NO_CONNECTION = 69
#: The exit code when the platform closed the connection before answering.
CONNECTION_CLOSED = 70
#: The exit code when the platform could not be reached.
UNREACHABLE = 75

#: The trailer an AI session adds to each commit it writes.
CO_AUTHOR = "Co-authored-by: Dooservice <noreply@dooservice.sh>"
#: The hook git runs to prepare a commit message.
PREPARE_COMMIT_MSG = "prepare-commit-msg"

#: The name of each language the console speaks, in English, for the agent's instructions.
LANGUAGE_NAMES = {
    "es": "Spanish",
    "en": "English",
    "pt": "Portuguese",
    "fr": "French",
    "it": "Italian",
    "de": "German",
}
#: Ctrl+Z as the terminal sends it; it never reaches the agent.
CTRL_Z = b"\x1a"
#: What the agent receives instead of Ctrl+Z.
NUL = b"\x00"
#: How often the splash draws a frame.
FRAME_SECONDS = 0.1
#: How much of the agent's recent output is kept to find a login URL in.
SEEN_BYTES = 16 * 1024
#: The most bytes read from the agent's terminal at once.
READ_BYTES = 65536
#: The most bytes read from the person's keyboard at once.
KEYS_BYTES = 1024
#: Where the login pages of the AI tools start.
LOGIN_URLS = (
    b"https://console.anthropic.com/oauth/authorize",
    b"https://claude.ai/oauth/authorize",
    b"https://platform.claude.com/oauth/authorize",
    b"https://claude.com/cai/oauth/authorize",
    b"https://auth.openai.com/oauth/authorize",
)
#: Words a tool prints after a login URL, which plainly are not part of it.
URL_TERMINATORS = {b"authorization", b"code", b"enter", b"submit", b"esc", b"paste", b"here"}
#: The OSC 9 sequence that announces a URL to the browser, before its base64 body.
ANNOUNCE_OPEN = b"\x1b]9;"
#: The end of the announcement.
ANNOUNCE_CLOSE = b"\x07"

#: The dooservice logo, line by line.
LOGO = (
    "     _                                   _",
    "  __| | ___   ___  ___  ___ _ ____   __(_) ___ ___",
    " / _` |/ _ \\ / _ \\/ __|/ _ \\ '__\\ \\ / /| |/ __/ _ \\",
    "| (_| | (_) | (_) \\__ \\  __/ |   \\ V / | | (_|  __/",
    " \\__,_|\\___/ \\___/|___/\\___|_|    \\_/  |_|\\___\\___|",
)
#: The frames of the splash's spinner.
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
#: Dooservice's teal, as red, green and blue.
TEAL = (98, 184, 195)
#: White, as red, green and blue.
WHITE = (255, 255, 255)
#: Gray text.
GRAY = "\033[38;2;110;118;129m"
#: Back to the terminal's own colours.
RESET = "\033[0m"
#: The width of the splash's progress bar.
BAR_WIDTH = 24
#: How long the splash plays at least, whichever tool it is.
MINIMUM_SECONDS = 5
#: The terminal size assumed when there is none, as columns and rows.
DEFAULT_TERMINAL_SIZE = (80, 24)
#: "Starting", in each language the console speaks other than English.
STARTING = {"es": "Iniciando", "pt": "Iniciando", "fr": "Démarrage de", "it": "Avvio di", "de": "Starte"}
#: "Starting" in English, and when the language is none of those.
STARTING_DEFAULT = "Starting"

#: The escape byte that opens every terminal sequence, read by `terminal`.
ESC = 0x1B
#: The bell, which ends an OSC sequence.
BEL = 0x07
#: The byte after ESC that opens a CSI sequence.
CSI_OPEN = ord("[")
#: The byte after ESC that opens an OSC sequence.
OSC_OPEN = ord("]")
#: The byte after ESC that ends a string sequence.
STRING_TERMINATOR = ord("\\")
#: DCS, SOS, PM and APC: strings a terminal answers or keeps, run up to the string terminator.
CONTROL_STRING_OPENS = frozenset(b"PX^_")
#: How an OSC 8 hyperlink starts.
HYPERLINK = b"8;"
#: How a secure URL starts.
SECURE_URL = b"https://"
#: CSI parameter bytes, inclusive.
CSI_PARAMETERS = (0x30, 0x3F)
#: Intermediate bytes of CSI and other escape sequences, inclusive.
INTERMEDIATES = (0x20, 0x2F)
#: CSI final bytes, inclusive.
CSI_FINALS = (0x40, 0x7E)
#: The highest byte that is not printable text.
LAST_BLANK = 0x20
