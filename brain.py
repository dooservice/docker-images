"""The commit of dooservice/odoo-brain an Odoo version's image carries, from odoo/brain.toml.

    python3 brain.py odoo/brain.toml 19.0
    python3 brain.py odoo/brain.toml --check 16.0 17.0 18.0 19.0 20.0
"""

import sys
import tomllib
from pathlib import Path

HEX = frozenset("0123456789abcdef")
COMMIT_LENGTH = 40


class BrainCommits:
    def __init__(self, path):
        self.commits = tomllib.loads(Path(path).read_text()).get("commits", {})

    def of(self, version):
        commit = str(self.commits.get(version, ""))
        if len(commit) != COMMIT_LENGTH or not set(commit) <= HEX:
            raise SystemExit(f"odoo/brain.toml has no full commit for Odoo {version}")
        return commit


if __name__ == "__main__":
    commits = BrainCommits(sys.argv[1])
    if sys.argv[2] == "--check":
        for version in sys.argv[3:]:
            commits.of(version)
    else:
        print(commits.of(sys.argv[2]))
