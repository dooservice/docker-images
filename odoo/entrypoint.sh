#!/bin/bash
set -e

for addons in /mnt/addons /mnt/extra-addons; do
    [ -d "${addons}" ] || continue
    while IFS= read -r -d '' req; do
        echo "[dooservice] Installing ${req}..."
        pip install --no-cache-dir --break-system-packages -q -r "${req}" || true
    done < <(find "${addons}" -name requirements.txt -print0 2>/dev/null)
done

exec "$@"
