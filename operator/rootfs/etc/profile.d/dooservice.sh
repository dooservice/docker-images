# dooservice console: environment, welcome banner and prompt.
#
# Sourced by every login shell, so it sets no shell options: `set -e` here would close
# the person's shell at the first command that fails.

export EDITOR=vim.tiny
export VISUAL=$EDITOR
export LESS="--ignore-case --LONG-PROMPT --RAW-CONTROL-CHARS --tabs=4 --no-init --window=-4"
export XDG_CONFIG_HOME=$HOME/.config
export XDG_CACHE_HOME=$HOME/.cache

[ -z "${PS1:-}" ] && return

alias ls='ls --color=auto'
alias l='LC_ALL=C ls -lAh'
alias ll='LC_ALL=C ls -lA | less -r -E -X'
alias grep='grep --color=auto'
alias g='git'

case "${DOOSERVICE_STAGE:-}" in
    production) dooservice_stage="prod"; dooservice_color='\[\e[91m\]' ;;
    development) dooservice_stage="dev"; dooservice_color='\[\e[38;2;98;184;195m\]' ;;
    *) dooservice_stage="${DOOSERVICE_STAGE:-}"; dooservice_color='\[\e[97m\]' ;;
esac
PS1="${dooservice_color}${DOOSERVICE_ENVIRONMENT:-dooservice}\[\e[0m\] \[\e[90m\][${dooservice_stage}/${ODOO_VERSION:-}]\[\e[0m\]:\w\$ "
unset dooservice_stage dooservice_color

python3 -m dooservice_console.welcome
