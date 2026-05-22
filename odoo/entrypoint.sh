#!/bin/bash
set -e

if [ -d "/mnt/extra-addons" ]; then
    while IFS= read -r -d '' req; do
        echo "[dooservice] Installing ${req}..."
        pip install --no-cache-dir --break-system-packages -q -r "${req}" || true
    done < <(find /mnt/extra-addons -name requirements.txt -print0 2>/dev/null)
fi

exec "$@"
