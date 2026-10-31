"""Claude Code, set up for the environment this console belongs to.

The binary in /opt/ai is Claude Code as Anthropic ships it; everything dooservice adds is
arguments and a few files. The project is the environment's addons, or the session's
home when there is no repository and the agent only configures; the settings, the
instructions and the skills come from /opt/dooservice/ai and cannot be changed from
here — the instructions reach it as `~/.claude/CLAUDE.md`, which imports them — and each
person signs in with their own account: the login lives in this session's home and is
gone when the session ends.

The conversations are kept: `~/.claude/projects` is the person's own directory for this
environment, which the platform mounts into their consoles and nobody else's, and the
last one is picked up unless a new one was asked for.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess

from .ai import AiSession
from .constants import (
    AI_DIR,
    AI_LOG,
    CLAUDE_BINARY,
    CLAUDE_PASSTHROUGH,
    ENVIRONMENT_VARIABLE,
    HISTORY_VARIABLE,
    MCP_CONFIG,
    ODOO_SOURCE,
    ODOO_VERSION_VARIABLE,
    PROJECT_VARIABLE,
    RESUME_VARIABLE,
)
from .language import Language


class ClaudeLauncher:
    """Prepares the session's `~/.claude` and runs Claude Code with the environment's arguments."""

    def __init__(self, args):
        self.args = list(args)
        self.home = os.path.expanduser("~")
        self.claude_dir = os.path.join(self.home, ".claude")
        self.session = AiSession("claude")

    def run(self):
        self.session.begin()
        workspace = self.session.workspace
        os.makedirs(self.claude_dir, exist_ok=True)
        workspace.claude_memory(self.claude_dir)
        workspace.link_skills(os.path.join(self.claude_dir, "skills"))
        self.link_history()
        self.install_rtk()
        self.write_config(workspace.project)
        os.chdir(workspace.project)
        self.session.execute([CLAUDE_BINARY, *self.arguments()], "Claude Code")

    def link_history(self):
        """`~/.claude/projects` is the person's kept directory, when the platform mounts one."""
        kept = os.environ.get(HISTORY_VARIABLE, "")
        projects = os.path.join(self.claude_dir, "projects")
        if kept and not os.path.islink(projects) and not os.path.exists(projects):
            os.symlink(os.path.join(kept, "claude"), projects)

    def install_rtk(self):
        """rtk's instructions for Claude Code, once per session; a failure is not tried again."""
        marker = os.path.join(self.claude_dir, "RTK.md")
        if os.path.exists(marker):
            return
        try:
            with open(AI_LOG, "a") as log_file:
                subprocess.run(
                    ["rtk", "init", "-g", "--auto-patch"], input="n\n", text=True, stdout=log_file,
                    stderr=log_file, check=True,
                )
        except (OSError, subprocess.CalledProcessError):
            open(marker, "a").close()

    def write_config(self, project):
        """The trust dialog, already accepted for the project."""
        config_path = os.path.join(self.home, ".claude.json")
        if os.path.exists(config_path):
            return
        with open(config_path, "w") as config:
            json.dump({
                "hasTrustDialogAccepted": True,
                "theme": "dark",
                "projects": {project: {"hasTrustDialogAccepted": True, "allowedTools": []}},
            }, config)

    def arguments(self):
        """The person's arguments, and the environment's unless they asked for a subcommand."""
        args = list(self.args)
        if args and args[0] in CLAUDE_PASSTHROUGH:
            return args
        workspace = self.session.workspace
        version = os.environ.get(ODOO_VERSION_VARIABLE, "")
        environment = os.environ.get(ENVIRONMENT_VARIABLE, "")
        project = os.environ.get(PROJECT_VARIABLE, "")
        args += [
            f"--settings={workspace.claude_settings}",
            f"--mcp-config={MCP_CONFIG}",
            f"--add-dir={AI_DIR}/",
            f"--add-dir={ODOO_SOURCE}/",
            f"--append-system-prompt=Odoo version is {version}. This is the {environment} environment of the "
            f"{project} project on the dooservice platform, {workspace.describe()}. {Language().rule()}",
        ]
        history = os.path.join(self.claude_dir, "projects", workspace.project.replace("/", "-"))
        resume = os.environ.get(RESUME_VARIABLE, "1") != "0"
        if resume and glob.glob(os.path.join(history, "*.jsonl")):
            args.append("--continue")
        return args
