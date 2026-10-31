"""opencode, set up for the environment this console belongs to.

Same arrangement as the Claude Code launcher: the binary is untouched, the configuration
and the instructions come from /opt/dooservice/ai, and each person connects the provider
of their choice from inside the session. Its plugins arrive already installed, copied
from what the image prepared, instead of downloaded at every start.

The sessions are kept: `OPENCODE_DB` is in the person's own directory for this
environment, mounted into their consoles and nobody else's, while the login stays in this
session's home and goes with it. The last session is picked up unless a new one was asked
for.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess

from .ai import AiSession
from .constants import (
    AI_LOG,
    OPENCODE_BINARY,
    OPENCODE_CONFIG_VARIABLE,
    OPENCODE_DB_VARIABLE,
    OPENCODE_PASSTHROUGH,
    PLUGINS_TEMPLATE,
    RESUME_VARIABLE,
)
from .language import Language


class OpencodeLauncher:
    """Prepares the session's opencode configuration and runs opencode on the project."""

    def __init__(self, args):
        self.args = list(args)
        home = os.path.expanduser("~")
        self.session_config_dir = os.path.join(home, ".config", "dooservice")
        self.opencode_config_dir = os.path.join(home, ".config", "opencode")
        self.sessions_db = os.environ.get(OPENCODE_DB_VARIABLE) or os.path.join(
            home,
            ".local",
            "share",
            "opencode",
            "opencode.db",
        )
        self.session = AiSession("opencode")

    def run(self):
        self.session.begin()
        if not os.path.exists(self.opencode_config_dir) and os.path.isdir(PLUGINS_TEMPLATE):
            shutil.copytree(PLUGINS_TEMPLATE, self.opencode_config_dir, symlinks=True)
        self.session.workspace.link_skills(os.path.join(self.opencode_config_dir, "skills"))
        self.install_rtk()
        os.environ[OPENCODE_CONFIG_VARIABLE] = self.write_config()
        self.session.execute([OPENCODE_BINARY, *self.arguments()], "opencode")

    def install_rtk(self):
        """rtk's plugin for opencode, once per session."""
        if os.path.exists(os.path.join(self.opencode_config_dir, "plugins", "rtk.ts")):
            return
        try:
            with open(AI_LOG, "a") as log_file:
                subprocess.run(
                    ["rtk", "init", "-g", "--opencode"],
                    input="n\n",
                    text=True,
                    stdout=log_file,
                    stderr=log_file,
                    check=False,
                )
        except OSError:
            pass

    def write_config(self):
        """The image's configuration for this case, plus the language rule; returns its path."""
        os.makedirs(self.session_config_dir, exist_ok=True)
        language_file = os.path.join(self.session_config_dir, "LANGUAGE.md")
        with open(language_file, "w") as rule:
            rule.write(f"# Language\n\n{Language().rule()}\n")
        with open(self.session.workspace.opencode_config) as managed:
            config = json.load(managed)
        config["instructions"] = [*config.get("instructions", []), language_file]
        session_config = os.path.join(self.session_config_dir, "opencode.json")
        with open(session_config, "w") as generated:
            json.dump(config, generated)
        return session_config

    def arguments(self):
        """The person's arguments, then the project and `--continue` unless they asked for a subcommand."""
        args = list(self.args)
        if args and args[0] in OPENCODE_PASSTHROUGH:
            return args
        args.append(self.session.workspace.project)
        if os.environ.get(RESUME_VARIABLE, "1") != "0" and self.has_sessions():
            args.append("--continue")
        return args

    def has_sessions(self):
        if not os.path.exists(self.sessions_db):
            return False
        try:
            with sqlite3.connect(self.sessions_db) as connection:
                return connection.execute("SELECT COUNT(*) FROM session").fetchone()[0] > 0
        except sqlite3.Error:
            return False
