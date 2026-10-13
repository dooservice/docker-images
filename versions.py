"""The Odoo versions to build, one per line: the keys of `[odoo]` in the agent's platform.toml.

    python3 versions.py ../dooservice-agent/platform.toml
"""

import sys
import tomllib
from pathlib import Path

print("\n".join(tomllib.loads(Path(sys.argv[1]).read_text())["odoo"]))
