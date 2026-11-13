#!/bin/bash
# Installs the Python requirements of every addon in /mnt/addons, the project's repository,
# then runs the command. A requirements.txt that pip cannot install is logged as an ERROR
# with pip's output, and Odoo still starts, without those dependencies.
#
# A restart of the same container skips pip when no requirements.txt changed since it last
# installed them all: a deployment restarts Odoo, and asking pip again, over the network,
# lengthened every one of them. The mark lives in the container's own layer, never in a
# volume, so a new container installs everything again.
#
# PIP_BREAK_SYSTEM_PACKAGES instead of --break-system-packages: the pip of Odoo 16.0 does
# not know the option and refuses it, but ignores the variable.
set -euo pipefail

readonly ADDONS=/mnt/addons
readonly INSTALLED=/tmp/.dooservice-requirements

if [ -d "${ADDONS}" ]; then
    mapfile -d '' files < <(find "${ADDONS}" -name requirements.txt -print0 2>/dev/null | sort -z)
    wanted="$( (for requirements in "${files[@]}"; do echo "${requirements}"; cat "${requirements}"; done) | sha256sum | cut -d' ' -f1)"
    if [ -f "${INSTALLED}" ] && [ "$(cat "${INSTALLED}")" = "${wanted}" ]; then
        echo "[dooservice] Requirements unchanged since they were installed; pip is not asked."
    else
        complete=1
        for requirements in "${files[@]}"; do
            echo "[dooservice] Installing ${requirements}..."
            if ! output="$(PIP_BREAK_SYSTEM_PACKAGES=1 pip install --no-cache-dir -q -r "${requirements}" 2>&1)"; then
                complete=0
                echo "[dooservice] ERROR: could not install ${requirements}; Odoo starts without these dependencies." >&2
                echo "${output}" >&2
            fi
        done
        if [ "${complete}" = 1 ]; then
            echo "${wanted}" > "${INSTALLED}"
        fi
    fi
fi

exec "$@"
