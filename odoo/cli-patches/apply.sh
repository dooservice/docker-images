#!/bin/bash
# Gives Odoo 16.0, 17.0 and 18.0 the `odoo db` command of 19.0, so the agent runs the same
# database commands on every version: cli_db.py replaces odoo/cli/db.py, and
# service_db_wrapper.py lets odoo/service/db.py dump a database without its filestore.
#
# The Python files here are copied from Odoo and follow Odoo's code, not this repository's
# rules: leave them as close to Odoo's as possible.
set -euo pipefail

readonly VERSION="$1"
readonly PATCHES=/tmp/cli-patches
readonly ODOO_PATH=/usr/lib/python3/dist-packages/odoo

case "${VERSION}" in
  16.0|17.0) readonly CLI="v16-v17" ;;
  18.0) readonly CLI="v18" ;;
  *)
    echo "[dooservice] Odoo ${VERSION} already has every database command, nothing to patch."
    exit 0
    ;;
esac

echo "[dooservice] Patching the database commands of Odoo ${VERSION}..."
cp "${PATCHES}/${CLI}/cli_db.py" "${ODOO_PATH}/cli/db.py"
python3 "${PATCHES}/service_db_wrapper.py" "${ODOO_PATH}/service/db.py"
echo "[dooservice] Database commands patched."
