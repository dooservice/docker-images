#!/bin/bash
set -e

# ─── Install pip dependencies from addon requirements.txt ───
if [ -d "/mnt/extra-addons" ]; then
    REQ_FILES=$(find /mnt/extra-addons -name requirements.txt 2>/dev/null || true)
    if [ -n "$REQ_FILES" ]; then
        echo "[dooservice] Installing addon dependencies..."
        for f in $REQ_FILES; do
            pip install --no-cache-dir --break-system-packages -r "$f" 2>&1 || true
        done
        echo "[dooservice] Dependencies installed."
    fi
fi

# ─── Start Odoo (exec replaces shell, forwards signals) ───
exec "$@"
