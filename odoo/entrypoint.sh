#!/bin/bash
# Installs the Python requirements of every addon in /mnt/addons, the project's repository,
# then runs the command. A requirements.txt that pip cannot install is logged as an ERROR
# with pip's output, and Odoo still starts, without those dependencies.
#
# PIP_BREAK_SYSTEM_PACKAGES instead of --break-system-packages: the pip of Odoo 16.0 does
# not know the option and refuses it, but ignores the variable.
set -euo pipefail

readonly ADDONS=/mnt/addons

if [ -d "${ADDONS}" ]; then
    while IFS= read -r -d '' requirements; do
        echo "[dooservice] Installing ${requirements}..."
        if ! output="$(PIP_BREAK_SYSTEM_PACKAGES=1 pip install --no-cache-dir -q -r "${requirements}" 2>&1)"; then
            echo "[dooservice] ERROR: could not install ${requirements}; Odoo starts without these dependencies." >&2
            echo "${output}" >&2
        fi
    done < <(find "${ADDONS}" -name requirements.txt -print0 2>/dev/null)
fi

exec "$@"
