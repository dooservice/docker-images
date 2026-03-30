#!/bin/bash
set -e

VERSION=$1
ODOO_PATH=/usr/lib/python3/dist-packages/odoo

echo "[dooservice] Applying CLI patches for Odoo ${VERSION}..."

case $VERSION in
  16.0|17.0)
    cp /tmp/cli-patches/v16-v17/cli_db.py $ODOO_PATH/cli/db.py
    cp /tmp/cli-patches/v16-v17/service_db_wrapper.py /tmp/_patch_db.py
    python3 /tmp/_patch_db.py $ODOO_PATH/service/db.py
    rm /tmp/_patch_db.py
    ;;
  18.0)
    cp /tmp/cli-patches/v18/cli_db.py $ODOO_PATH/cli/db.py
    cp /tmp/cli-patches/v18/service_db_wrapper.py /tmp/_patch_db.py
    python3 /tmp/_patch_db.py $ODOO_PATH/service/db.py
    rm /tmp/_patch_db.py
    ;;
  19.0)
    echo "[dooservice] v19 already has all CLI commands, skipping."
    ;;
  *)
    echo "[dooservice] Unknown version ${VERSION}, skipping CLI patches."
    ;;
esac

echo "[dooservice] CLI patches applied."
