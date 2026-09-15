# dooservice console: environment, welcome banner and prompt.

export EDITOR=vim.tiny
export VISUAL=$EDITOR
export LESS="--ignore-case --LONG-PROMPT --RAW-CONTROL-CHARS --tabs=4 --no-init --window=-4"
export XDG_CONFIG_HOME=$HOME/.config
export XDG_CACHE_HOME=$HOME/.cache

[ -z "$PS1" ] && return

alias ls='ls --color=auto'
alias l='LC_ALL=C ls -lAh'
alias ll='LC_ALL=C ls -lA | less -r -E -X'
alias grep='grep --color=auto'
alias g='git'

case "$DOOSERVICE_STAGE" in
    production) __dooservice_stage="prod"; __dooservice_color='\[\e[91m\]' ;;
    development) __dooservice_stage="dev"; __dooservice_color='\[\e[38;2;98;184;195m\]' ;;
    *) __dooservice_stage="$DOOSERVICE_STAGE"; __dooservice_color='\[\e[97m\]' ;;
esac
PS1="${__dooservice_color}${DOOSERVICE_ENVIRONMENT:-dooservice}\[\e[0m\] \[\e[90m\][${__dooservice_stage}/${ODOO_VERSION}]\[\e[0m\]:\w\$ "
unset __dooservice_stage __dooservice_color

python3 - << 'EOF'
import os
import sys

if not sys.stdout.isatty() or os.path.exists(os.path.expanduser("~/.hushlogin")):
    sys.exit(0)

TEAL = "\033[38;2;98;184;195m"
WHITE = "\033[97;1m"
GRAY = "\033[90m"
RED = "\033[91;1m"
RESET = "\033[0m"

logo = r"""
     _                                   _
  __| | ___   ___  ___  ___ _ ____   __(_) ___ ___
 / _` |/ _ \ / _ \/ __|/ _ \ '__\ \ / /| |/ __/ _ \
| (_| | (_) | (_) \__ \  __/ |   \ V / | | (_|  __/
 \__,_|\___/ \___/|___/\___|_|    \_/  |_|\___\___|
""".strip("\n")

stage = os.environ.get("DOOSERVICE_STAGE", "")
stage_label = {"development": "desarrollo", "production": "producción"}.get(stage, stage)
stage_color = RED if stage == "production" else TEAL
project = os.environ.get("DOOSERVICE_PROJECT", "")
environment = os.environ.get("DOOSERVICE_ENVIRONMENT", "")
server = os.environ.get("DOOSERVICE_SERVER", "")
version = os.environ.get("ODOO_VERSION", "")

commands = [
    ("claude", "Claude Code con tu cuenta"),
    ("opencode", "opencode con tu proveedor"),
    ("dooservice shell", "Shell de Odoo sobre esta base"),
    ("dooservice update <módulos>", "Actualizar módulos"),
    ("dooservice install <módulos>", "Instalar módulos"),
    ("dooservice test <módulos>", "Ejecutar los tests de un módulo"),
    ("dooservice restart", "Reiniciar el Odoo de este entorno"),
    ("dooservice logs -f", "Seguir el log de Odoo"),
    ("dooservice storage", "Ver lo que ocupa el entorno"),
    ("psql", "Base de datos del entorno"),
]
configuration_only = not os.path.isdir("/mnt/extra-addons/.git")
if configuration_only:
    commands = [
        (name, f"{description}, modo configuración") if name in ("claude", "opencode") else (name, description)
        for name, description in commands
    ]

width = max(len(name) for name, _ in commands) + 4
lines = [f"{TEAL}{logo}{RESET}", ""]
lines.append(f"Estás en {WHITE}{project}{RESET} · entorno {stage_color}{stage_label}{RESET} {WHITE}{environment}{RESET}")
lines.append(f"{WHITE}Odoo {version}{RESET} · servidor {WHITE}{server}{RESET} · sesión auditada")
lines.append("")
lines.append(f"{WHITE}Comandos útiles:{RESET}")
lines.append("")
for name, description in commands:
    lines.append(f"  {WHITE}${RESET} {TEAL}{name.ljust(width)}{RESET}{description}")
lines.append("")
if configuration_only:
    lines.append(f"{GRAY}Sin repositorio: la IA configura Odoo, pero no crea ni modifica módulos.{RESET}")
lines.append(f"{GRAY}La sesión se cierra tras 30 minutos sin actividad.{RESET}")
print("\n".join(lines) + "\n")
EOF
