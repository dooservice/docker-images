"""Patch service/db.py to add with_filestore param to dump_db.

Exact text replacements: a block that is not found stops the build instead of leaving
the image unpatched.
"""
import sys

filepath = sys.argv[1]
with open(filepath, 'r') as fh:
    source = fh.read()

SIGNATURE = "def dump_db(db_name, stream, backup_format='zip'):"
PATCHED_SIGNATURE = "def dump_db(db_name, stream, backup_format='zip', with_filestore=True):"
FILESTORE = (
    "            filestore = odoo.tools.config.filestore(db_name)\n"
    "            if os.path.exists(filestore):\n"
    "                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))\n"
)
PATCHED_FILESTORE = "            if with_filestore:\n" + "".join(
    "    " + line for line in FILESTORE.splitlines(keepends=True)
)

for original, patched in ((SIGNATURE, PATCHED_SIGNATURE), (FILESTORE, PATCHED_FILESTORE)):
    if source.count(original) != 1:
        sys.exit(f"[dooservice] {filepath}: expected the block to patch once, found {source.count(original)}")
    source = source.replace(original, patched)

with open(filepath, 'w') as fh:
    fh.write(source)

print(f"[dooservice] Patched {filepath}")
