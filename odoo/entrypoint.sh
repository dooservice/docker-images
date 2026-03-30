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

# ─── Initialize database if requested and not yet done ───
MARKER="/var/lib/odoo/.dooservice_db_initialized"
if [ "$DOOSERVICE_INIT_DB" = "1" ] && [ ! -f "$MARKER" ]; then
    echo "[dooservice] Initializing database: $DB_NAME"
    INIT_CMD="odoo db init $DB_NAME --language $DB_LANGUAGE"
    [ -n "$DOOSERVICE_ADMIN_USER" ] && INIT_CMD="$INIT_CMD --username $DOOSERVICE_ADMIN_USER"
    [ -n "$DOOSERVICE_ADMIN_PASS" ] && INIT_CMD="$INIT_CMD --password $DOOSERVICE_ADMIN_PASS"
    if eval "$INIT_CMD"; then
        touch "$MARKER"
        echo "[dooservice] Database initialized."
    else
        echo "[dooservice] WARNING: Database init failed, continuing anyway."
    fi
fi

# ─── Start Odoo (exec replaces shell, forwards signals) ───
exec "$@"
