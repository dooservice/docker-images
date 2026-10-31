"""The Odoo versions to build, one per line: the keys of `[odoo]` in the agent's platform.toml.

python3 versions.py ../dooservice-agent/platform.toml
"""

from pathlib import Path
import sys
import tomllib

print("\n".join(tomllib.loads(Path(sys.argv[1]).read_text())["odoo"]))
