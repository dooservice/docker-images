"""The AI tools' settings, merged at build time from a base per tool and a few overlays.

Each tool has one base with what every case shares and an overlay per case (development,
no repository, production; Claude Code's development and no-repository cases also share
`unattended`). The merge is plain: objects merge key by key, lists are joined in order
without repeating an entry, and any other value of a later layer replaces the earlier one.

It runs in the Dockerfile, not at session start: the merged files are root's, in the
image, where a session — the agent included — can read them and cannot loosen them.
"""

from __future__ import annotations

import json
import os

from .constants import LAYERS_DIR, SETTINGS_FILES, SETTINGS_LAYERS


class SettingsLayers:
    """Merges the layers of each tool and case, and writes the files the launchers use."""

    def __init__(self, layers_dir=LAYERS_DIR):
        self.layers_dir = layers_dir

    def settings(self, tool, case):
        """The merged settings of one tool for one case."""
        merged = {}
        for layer in SETTINGS_LAYERS[tool][case]:
            with open(os.path.join(self.layers_dir, tool, f"{layer}.json")) as source:
                merged = self.merge(merged, json.load(source))
        return merged

    @classmethod
    def merge(cls, earlier, later):
        """`later` laid over `earlier`, without changing either."""
        if isinstance(earlier, dict) and isinstance(later, dict):
            merged = dict(earlier)
            for name, value in later.items():
                merged[name] = cls.merge(earlier[name], value) if name in earlier else value
            return merged
        if isinstance(earlier, list) and isinstance(later, list):
            return earlier + [item for item in later if item not in earlier]
        return later

    def write(self, files=None):
        """Every tool's settings for every case, at the paths the launchers read."""
        for tool, cases in (files or SETTINGS_FILES).items():
            for case, path in cases.items():
                with open(path, "w") as target:
                    json.dump(self.settings(tool, case), target, indent=4)
                    target.write("\n")
