"""Modules, the log and the reference, as tools: what the `dooservice` command does, with
its output trimmed to what an agent needs to read."""

import os
import subprocess

from dooservice_console.constants import DOOSERVICE_COMMAND, ODOO_SOURCE

from .constants import (
    COMMAND_TIMEOUT_SECONDS,
    LOG_LINES,
    LOG_LINES_MAXIMUM,
    LOGS_TIMEOUT_SECONDS,
    MATCH_WIDTH,
    REFERENCE,
    SOURCE_MATCHES,
    TAIL,
)
from .gate import Gate
from .refusal import ToolRefused
from .tool import Tool

gate = Gate()


class Command:
    """A console command run for a tool, its output trimmed."""

    @staticmethod
    def run(*args, timeout=COMMAND_TIMEOUT_SECONDS):
        try:
            done = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as late:
            raise ToolRefused(f"{' '.join(args)} did not finish within {timeout} seconds.") from late
        output = "\n".join((done.stdout + done.stderr).strip().splitlines()[-TAIL:])
        if done.returncode != 0:
            raise ToolRefused(f"{' '.join(args[1:])} failed:\n{output}")
        return output or "Done."


class ModuleInstall(Tool):
    """Modules installed with `dooservice install`."""

    name = "module_install"
    description = "Install modules (comma-separated) in this database. Restart afterwards for Python code."
    schema = {"modules": {"type": "string"}}
    required = ("modules",)

    def run(self, arguments):
        gate.ensure_modules_allowed()
        return Command.run(DOOSERVICE_COMMAND, "install", arguments["modules"])


class ModuleUpdate(ModuleInstall):
    """Modules updated with `dooservice update`."""

    name = "module_update"
    description = "Update modules (comma-separated) in this database after their code or data changed."

    def run(self, arguments):
        gate.ensure_modules_allowed()
        return Command.run(DOOSERVICE_COMMAND, "update", arguments["modules"])


class OdooLogs(Tool):
    """The environment's Odoo log."""

    name = "odoo_logs"
    description = "The last lines of this environment's Odoo log, errors included."
    schema = {"lines": {"type": "integer"}}

    def run(self, arguments):
        lines = min(int(arguments.get("lines") or LOG_LINES), LOG_LINES_MAXIMUM)
        return Command.run(DOOSERVICE_COMMAND, "logs", "-n", str(lines), timeout=LOGS_TIMEOUT_SECONDS)


class OdooFind(Tool):
    """A text search of the reference or of Odoo's source."""

    name = "odoo_find"
    description = (
        "Search the odoo-reference of this version (models, fields, settings, XML ids) and, with source=true, "
        "Odoo's own source. Returns matching lines with their file."
    )
    schema = {"text": {"type": "string"}, "source": {"type": "boolean"}}
    required = ("text",)

    def run(self, arguments):
        where = ODOO_SOURCE if arguments.get("source") else REFERENCE
        if not os.path.isdir(where):
            raise ToolRefused(f"{where} is not in this image.")
        found = subprocess.run(
            ["grep", "-rnF", "--include=*.md", "--include=*.py", "--include=*.xml", arguments["text"], where],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.splitlines()
        shown = [line.replace(where + "/", "")[:MATCH_WIDTH] for line in found[:SOURCE_MATCHES]]
        more = f"\n… {len(found) - SOURCE_MATCHES} more" if len(found) > SOURCE_MATCHES else ""
        return "\n".join(shown) + more if shown else "Nothing found."
