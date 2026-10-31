"""The production rules of the AI tools' settings, checked on the merged layers.

A later edit of a base or an overlay must not loosen production. Run from the
repository's root:

    PYTHONPATH=operator/rootfs/opt/dooservice/lib python3 -m unittest discover -s operator/tests
"""

import os
import unittest

from dooservice_console.constants import DEVELOPMENT, NO_REPOSITORY, PRODUCTION
from dooservice_console.settings import SettingsLayers

LAYERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rootfs", "opt", "dooservice", "ai", "layers")


class ProductionSettingsTest(unittest.TestCase):
    """Claude Code and opencode on production: read freely, ask before running, never write or reach the credentials."""

    def setUp(self):
        self.layers = SettingsLayers(LAYERS)

    def test_claude_production_denies(self):
        permissions = self.layers.settings("claude", PRODUCTION)["permissions"]
        for rule in (
            "Edit",
            "Write",
            "NotebookEdit",
            "Read(/run/dooservice/**)",
            "Bash(*/run/dooservice*)",
            "Bash(*write-credentials*)",
            "mcp__dooservice__module_install",
            "mcp__dooservice__module_update",
        ):
            self.assertIn(rule, permissions["deny"])

    def test_claude_production_asks(self):
        settings = self.layers.settings("claude", PRODUCTION)
        permissions = settings["permissions"]
        self.assertEqual(permissions["defaultMode"], "default")
        self.assertNotIn("skipDangerousModePermissionPrompt", settings)
        for rule in ("Bash(odoo-bin:*)", "Bash(python3:*)", "Bash(dooservice shell:*)", "mcp__dooservice__odoo_write"):
            self.assertIn(rule, permissions["ask"])
            self.assertNotIn(rule, permissions["allow"])
        for rule in ("Bash(dooservice:*)", "Bash(sed *)", "Bash(git:*)", "mcp__dooservice"):
            self.assertNotIn(rule, permissions["allow"])
        for command in ("head", "grep", "tail", "wc", "cat", "find"):
            self.assertFalse([rule for rule in permissions["allow"] if rule.startswith(f"Bash({command}")])

    def test_opencode_production(self):
        settings = self.layers.settings("opencode", PRODUCTION)
        permission = settings["permission"]
        self.assertEqual(permission["edit"], "deny")
        self.assertEqual(permission["read"]["/run/dooservice/*"], "deny")
        self.assertEqual(permission["external_directory"]["/run/dooservice/*"], "deny")
        bash = list(permission["bash"].items())
        self.assertEqual(bash[0], ("*", "ask"))
        self.assertEqual(bash[-2:], [("*/run/dooservice*", "deny"), ("*write-credentials*", "deny")])
        self.assertEqual(
            [pattern for pattern, action in bash if action == "allow"],
            ["psql*", "dooservice status", "dooservice logs*", "dooservice storage", "ls*", "echo*"],
        )
        self.assertEqual(permission["dooservice_odoo_write"], "ask")
        self.assertEqual(permission["dooservice_odoo_settings"], "ask")
        self.assertIs(settings["tools"]["dooservice_module_*"], False)

    def test_other_cases(self):
        self.assertIn("Edit", self.layers.settings("claude", NO_REPOSITORY)["permissions"]["deny"])
        self.assertNotIn("deny", self.layers.settings("claude", DEVELOPMENT)["permissions"])
        self.assertEqual(self.layers.settings("opencode", NO_REPOSITORY)["permission"]["edit"], "deny")
        self.assertEqual(self.layers.settings("opencode", DEVELOPMENT)["permission"], "allow")


if __name__ == "__main__":
    unittest.main()
