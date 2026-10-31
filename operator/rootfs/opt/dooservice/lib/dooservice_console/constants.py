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
#: The layers each settings file is merged from at build time: a base per tool and overlays.
LAYERS_DIR = f"{AI_DIR}/layers"
#: The layers of each tool's settings, by case, in the order they are merged.
SETTINGS_LAYERS = {
    "claude": {
        DEVELOPMENT: ("base", "unattended", DEVELOPMENT),
        NO_REPOSITORY: ("base", "unattended", NO_REPOSITORY),
        PRODUCTION: ("base", PRODUCTION),
    },
    "opencode": {
        DEVELOPMENT: ("base", DEVELOPMENT),
        NO_REPOSITORY: ("base", NO_REPOSITORY),
        PRODUCTION: ("base", PRODUCTION),
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

#: Seconds without activity before the platform closes the session, as the platform passes it.
IDLE_SECONDS_VARIABLE = "DOOSERVICE_IDLE_SECONDS"
#: The most seconds a session lasts, as the platform passes it.
MAX_SECONDS_VARIABLE = "DOOSERVICE_MAX_SECONDS"
#: A person who wants no welcome leaves this file in their home.
HUSHLOGIN = "~/.hushlogin"
#: The welcome's colours: teal, bold white, gray and bold red.
WELCOME_COLOURS = {
    "teal": "\033[38;2;98;184;195m",
    "white": "\033[97;1m",
    "gray": "\033[90m",
    "red": "\033[91;1m",
}
#: The welcome's commands, each with the key of its description in `WELCOME_TEXTS`.
WELCOME_COMMANDS = (
    ("claude", "claude"),
    ("opencode", "opencode"),
    ("dooservice shell", "shell"),
    ("dooservice update {modules}", "update"),
    ("dooservice install {modules}", "install"),
    ("dooservice test {modules}", "test"),
    ("dooservice restart", "restart"),
    ("dooservice logs -f", "logs"),
    ("dooservice storage", "storage"),
    ("psql", "psql"),
)
#: The language of the welcome when the person's is none of `WELCOME_TEXTS`.
WELCOME_DEFAULT = "en"
#: The welcome in each language the console speaks.
WELCOME_TEXTS = {
    "en": {
        DEVELOPMENT: "development",
        PRODUCTION: "production",
        "place": "You are in {project} · {stage} environment {environment}",
        "odoo": "{odoo} · server {server}",
        "commands": "Useful commands:",
        "modules": "<modules>",
        "claude": "Claude Code with your account",
        "opencode": "opencode with your provider",
        "shell": "Odoo shell on this database",
        "update": "Update modules",
        "install": "Install modules",
        "test": "Run a module's tests",
        "restart": "Restart this environment's Odoo",
        "logs": "Follow the Odoo log",
        "storage": "See what the environment occupies",
        "psql": "The environment's database",
        "no_repository": "No repository: the AI configures Odoo, but does not create or change modules.",
        "production_data": "PRODUCTION: real data. A backup of the database is being made: until it ends, read only.",
        "production_deploy": "No modules are installed and no code is published from here.",
        "idle": "The session closes after {minutes} minutes without activity.",
        "idle_unknown": "The session closes after a while without activity.",
        "limit": "It lasts {minutes} minutes at most.",
        "limit_unknown": "It has a time limit.",
    },
    "es": {
        DEVELOPMENT: "desarrollo",
        PRODUCTION: "producción",
        "place": "Estás en {project} · entorno {stage} {environment}",
        "odoo": "{odoo} · servidor {server}",
        "commands": "Comandos útiles:",
        "modules": "<módulos>",
        "claude": "Claude Code con tu cuenta",
        "opencode": "opencode con tu proveedor",
        "shell": "Shell de Odoo sobre esta base",
        "update": "Actualizar módulos",
        "install": "Instalar módulos",
        "test": "Ejecutar los tests de un módulo",
        "restart": "Reiniciar el Odoo de este entorno",
        "logs": "Seguir el log de Odoo",
        "storage": "Ver lo que ocupa el entorno",
        "psql": "Base de datos del entorno",
        "no_repository": "Sin repositorio: la IA configura Odoo, pero no crea ni modifica módulos.",
        "production_data": "PRODUCCIÓN: datos reales. Se está haciendo una copia de la base: hasta que termine, "
                           "solo lectura.",
        "production_deploy": "No se instalan módulos ni se publica código desde aquí.",
        "idle": "La sesión se cierra tras {minutes} minutos sin actividad.",
        "idle_unknown": "La sesión se cierra tras un tiempo sin actividad.",
        "limit": "Dura {minutes} minutos como máximo.",
        "limit_unknown": "Tiene una duración máxima.",
    },
    "pt": {
        DEVELOPMENT: "desenvolvimento",
        PRODUCTION: "produção",
        "place": "Você está em {project} · ambiente de {stage} {environment}",
        "odoo": "{odoo} · servidor {server}",
        "commands": "Comandos úteis:",
        "modules": "<módulos>",
        "claude": "Claude Code com a sua conta",
        "opencode": "opencode com o seu provedor",
        "shell": "Shell do Odoo nesta base de dados",
        "update": "Atualizar módulos",
        "install": "Instalar módulos",
        "test": "Executar os testes de um módulo",
        "restart": "Reiniciar o Odoo deste ambiente",
        "logs": "Acompanhar o log do Odoo",
        "storage": "Ver o que o ambiente ocupa",
        "psql": "Base de dados do ambiente",
        "no_repository": "Sem repositório: a IA configura o Odoo, mas não cria nem altera módulos.",
        "production_data": "PRODUÇÃO: dados reais. Está sendo feita uma cópia da base de dados: até terminar, "
                           "somente leitura.",
        "production_deploy": "Daqui não se instalam módulos nem se publica código.",
        "idle": "A sessão é encerrada após {minutes} minutos sem atividade.",
        "idle_unknown": "A sessão é encerrada após um tempo sem atividade.",
        "limit": "Dura no máximo {minutes} minutos.",
        "limit_unknown": "Tem uma duração máxima.",
    },
    "fr": {
        DEVELOPMENT: "développement",
        PRODUCTION: "production",
        "place": "Vous êtes dans {project} · environnement de {stage} {environment}",
        "odoo": "{odoo} · serveur {server}",
        "commands": "Commandes utiles :",
        "modules": "<modules>",
        "claude": "Claude Code avec votre compte",
        "opencode": "opencode avec votre fournisseur",
        "shell": "Shell Odoo sur cette base",
        "update": "Mettre à jour des modules",
        "install": "Installer des modules",
        "test": "Lancer les tests d'un module",
        "restart": "Redémarrer l'Odoo de cet environnement",
        "logs": "Suivre le journal d'Odoo",
        "storage": "Voir l'espace occupé par l'environnement",
        "psql": "Base de données de l'environnement",
        "no_repository": "Sans dépôt : l'IA configure Odoo, mais ne crée ni ne modifie de modules.",
        "production_data": "PRODUCTION : données réelles. Une copie de la base est en cours : jusqu'à la fin, "
                           "lecture seule.",
        "production_deploy": "Ici, on n'installe pas de modules et on ne publie pas de code.",
        "idle": "La session se ferme après {minutes} minutes d'inactivité.",
        "idle_unknown": "La session se ferme après un moment d'inactivité.",
        "limit": "Elle dure {minutes} minutes au maximum.",
        "limit_unknown": "Sa durée est limitée.",
    },
    "it": {
        DEVELOPMENT: "sviluppo",
        PRODUCTION: "produzione",
        "place": "Sei in {project} · ambiente di {stage} {environment}",
        "odoo": "{odoo} · server {server}",
        "commands": "Comandi utili:",
        "modules": "<moduli>",
        "claude": "Claude Code con il tuo account",
        "opencode": "opencode con il tuo provider",
        "shell": "Shell di Odoo su questo database",
        "update": "Aggiornare moduli",
        "install": "Installare moduli",
        "test": "Eseguire i test di un modulo",
        "restart": "Riavviare l'Odoo di questo ambiente",
        "logs": "Seguire il log di Odoo",
        "storage": "Vedere quanto occupa l'ambiente",
        "psql": "Database dell'ambiente",
        "no_repository": "Senza repository: l'IA configura Odoo, ma non crea né modifica moduli.",
        "production_data": "PRODUZIONE: dati reali. È in corso una copia del database: fino alla fine, sola lettura.",
        "production_deploy": "Da qui non si installano moduli né si pubblica codice.",
        "idle": "La sessione si chiude dopo {minutes} minuti di inattività.",
        "idle_unknown": "La sessione si chiude dopo un po' di inattività.",
        "limit": "Dura al massimo {minutes} minuti.",
        "limit_unknown": "Ha una durata massima.",
    },
    "de": {
        DEVELOPMENT: "Entwicklung",
        PRODUCTION: "Produktion",
        "place": "Du bist in {project} · Umgebung {environment} ({stage})",
        "odoo": "{odoo} · Server {server}",
        "commands": "Nützliche Befehle:",
        "modules": "<Module>",
        "claude": "Claude Code mit deinem Konto",
        "opencode": "opencode mit deinem Anbieter",
        "shell": "Odoo-Shell auf dieser Datenbank",
        "update": "Module aktualisieren",
        "install": "Module installieren",
        "test": "Die Tests eines Moduls ausführen",
        "restart": "Das Odoo dieser Umgebung neu starten",
        "logs": "Dem Odoo-Log folgen",
        "storage": "Anzeigen, wie viel die Umgebung belegt",
        "psql": "Datenbank der Umgebung",
        "no_repository": "Kein Repository: Die KI konfiguriert Odoo, erstellt oder ändert aber keine Module.",
        "production_data": "PRODUKTION: echte Daten. Die Datenbank wird gesichert: bis dahin nur lesen.",
        "production_deploy": "Von hier werden keine Module installiert und kein Code veröffentlicht.",
        "idle": "Die Sitzung wird nach {minutes} Minuten ohne Aktivität geschlossen.",
        "idle_unknown": "Die Sitzung wird nach einer Weile ohne Aktivität geschlossen.",
        "limit": "Sie dauert höchstens {minutes} Minuten.",
        "limit_unknown": "Sie hat eine Höchstdauer.",
    },
}

#: The tests run in this session with `dooservice test`, one JSON line per run; `publish` sends them.
TEST_RUNS = "~/.local/state/dooservice/tests.jsonl"
#: The exit code of a command stopped with Ctrl+C.
INTERRUPTED = 130
#: The exit code of a command refused because of how it was called.
USAGE = 2
