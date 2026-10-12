"""Modules, the log and the reference, as tools: what the `dooservice` command does, with
its output trimmed to what an agent needs to read."""

import os
import subprocess

from gate import Gate
from refusal import ToolRefused
from tool import Tool

DOOSERVICE = "/usr/local/bin/dooservice"
REFERENCE = "/opt/dooservice/ai/skills/code/odoo-reference"
ODOO_SOURCE = "/usr/lib/python3/dist-packages/odoo"
TAIL = 60
MATCHES = 80
gate = Gate()


class Command:
    @staticmethod
    def run(*args, timeout=900):
        try:
            done = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as late:
            raise ToolRefused(f"{' '.join(args)} did not finish within {timeout} seconds.") from late
        output = "\n".join((done.stdout + done.stderr).strip().splitlines()[-TAIL:])
        if done.returncode != 0:
            raise ToolRefused(f"{' '.join(args[1:])} failed:\n{output}")
        return output or "Done."


class ModuleInstall(Tool):
    name = "module_install"
    description = "Install modules (comma-separated) in this database. Restart afterwards for Python code."
    schema = {"modules": {"type": "string"}}
    required = ("modules",)

    def run(self, arguments):
        gate.ensure_modules_allowed()
        return Command.run(DOOSERVICE, "install", arguments["modules"])


class ModuleUpdate(ModuleInstall):
    name = "module_update"
    description = "Update modules (comma-separated) in this database after their code or data changed."

    def run(self, arguments):
        gate.ensure_modules_allowed()
        return Command.run(DOOSERVICE, "update", arguments["modules"])


class OdooLogs(Tool):
    name = "odoo_logs"
    description = "The last lines of this environment's Odoo log, errors included."
    schema = {"lines": {"type": "integer"}}

    def run(self, arguments):
        lines = min(int(arguments.get("lines") or 200), 1000)
        return Command.run(DOOSERVICE, "logs", "-n", str(lines), timeout=60)


class OdooFind(Tool):
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
            capture_output=True, text=True, check=False,
        ).stdout.splitlines()
        shown = [line.replace(where + "/", "")[:240] for line in found[:MATCHES]]
        more = f"\n… {len(found) - MATCHES} more" if len(found) > MATCHES else ""
        return "\n".join(shown) + more if shown else "Nothing found."
