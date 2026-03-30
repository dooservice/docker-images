"""Patch service/db.py to add with_filestore param to dump_db."""
import re
import sys

filepath = sys.argv[1]
with open(filepath, 'r') as fh:
    source = fh.read()

# Add with_filestore=True to dump_db signature
source = source.replace(
    "def dump_db(db_name, stream, backup_format='zip'):",
    "def dump_db(db_name, stream, backup_format='zip', with_filestore=True):",
)

# Wrap filestore copytree in with_filestore check
source = re.sub(
    r'(            filestore = odoo\.tools\.config\.filestore\(db_name\)\n)'
    r'(            if os\.path\.exists\(filestore\):\n)'
    r'(                shutil\.copytree\(filestore, os\.path\.join\(dump_dir, .filestore.\)\))',
    r'            if with_filestore:\n'
    r'    \1    \2    \3',
    source,
)

with open(filepath, 'w') as fh:
    fh.write(source)

print(f"[dooservice] Patched {filepath}")
