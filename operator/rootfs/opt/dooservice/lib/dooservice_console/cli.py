"""Work on this environment from its console.

What this container can do by itself runs here: installing, updating and testing modules,
opening an Odoo shell, measuring storage. What it cannot — restarting the environment,
reading its live log, publishing — is asked of the platform, which does it outside this
container and only for this environment.

`test` runs the tests as a child and records each run, so `publish` can list every test
run of the session in the pull request.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from .constants import DATA_DIR, INTERRUPTED, ODOO_WRAPPER, REPOSITORY, USAGE
from .control import ControlClient
from .production import Production
from .runs import TestRuns


class DooserviceCommand:
    """The `dooservice` command: its arguments, and what each subcommand does."""

    def __init__(self):
        self.platform = ControlClient()

    @staticmethod
    def parser():
        parser = argparse.ArgumentParser(prog="dooservice", description=__doc__.splitlines()[0])
        commands = parser.add_subparsers(dest="command", metavar="<command>")
        commands.required = True
        commands.add_parser("status", help="Show whether the environment is running")
        commands.add_parser("restart", help="Restart the environment's Odoo")
        logs = commands.add_parser("logs", help="Show the environment's Odoo log")
        logs.add_argument("-n", "--lines", type=int, default=200, help="How many lines to show (default 200)")
        logs.add_argument("-f", "--follow", action="store_true", help="Keep printing new lines until Ctrl+C")
        update = commands.add_parser("update", help="Update modules in the database")
        update.add_argument("modules", help="Comma-separated modules, or 'all'")
        install = commands.add_parser("install", help="Install modules in the database")
        install.add_argument("modules", help="Comma-separated modules")
        test = commands.add_parser("test", help="Run modules' tests; publish lists every run")
        test.add_argument("modules", help="Comma-separated modules")
        commands.add_parser("shell", help="Open an Odoo shell on this database")
        commands.add_parser("storage", help="Show what the environment occupies")
        publish = commands.add_parser(
            "publish",
            help="Publish what was committed as pull requests, or update this session's",
        )
        publish.add_argument("--title", required=True, help="The pull request's title: [TAG] module: summary")
        described = publish.add_mutually_exclusive_group(required=True)
        described.add_argument("--body", help="The pull request's description")
        described.add_argument("--body-file", help="Read the description from a file, or from stdin with '-'")
        publish.add_argument("--draft", action="store_true", help="Open the pull requests as drafts")
        return parser

    def run(self, argv):
        """Parse the arguments and run the subcommand; written without `match`, which Odoo 16's Python 3.9 lacks."""
        options = self.parser().parse_args(argv)
        actions = {
            "status": self.status,
            "restart": self.restart,
            "logs": self.logs,
            "update": self.modules,
            "install": self.modules,
            "test": self.test,
            "shell": self.shell,
            "storage": self.storage,
            "publish": self.publish,
        }
        actions[options.command](options)

    def status(self, options):
        self.platform.run("status")

    def restart(self, options):
        Production.require_changes("Restarting Odoo")
        self.platform.run("restart")

    def logs(self, options):
        try:
            self.platform.run("logs", {"lines": options.lines, "follow": options.follow})
        except KeyboardInterrupt:
            sys.exit(0)

    def modules(self, options):
        Production.refuse("Installing, updating or testing modules")
        flag = "-i" if options.command == "install" else "-u"
        self.odoo(flag, options.modules, "--stop-after-init")

    def test(self, options):
        """Update the modules with their tests, as a child, and record the run for `publish`."""
        Production.refuse("Installing, updating or testing modules")
        command = [ODOO_WRAPPER, "-u", options.modules, "--test-enable", "--stop-after-init"]
        try:
            code = TestRuns().run(options.modules, command)
        except KeyboardInterrupt:
            sys.exit(INTERRUPTED)
        sys.exit(code)

    def shell(self, options):
        self.odoo("shell")

    def publish(self, options):
        """Send the title, the description and this session's test runs; print what the platform answers."""
        Production.refuse("Publishing")
        title = options.title.strip()
        body = options.body
        if options.body_file:
            if options.body_file == "-":
                body = sys.stdin.read()
            else:
                with open(options.body_file) as described:
                    body = described.read()
        if not title:
            self.refuse('publish needs a title: --title "[TAG] module: summary".')
        if not body.strip():
            self.refuse('publish needs a description: --body "..." or --body-file FILE (- for stdin).')
        self.platform.run(
            "publish",
            {
                "title": title,
                "body": body,
                "draft": options.draft,
                "tests": TestRuns().all(),
            },
        )

    @staticmethod
    def refuse(message):
        sys.stderr.write(f"dooservice: {message}\n")
        sys.exit(USAGE)

    @staticmethod
    def odoo(*args):
        os.execv(ODOO_WRAPPER, [ODOO_WRAPPER, *args])

    @staticmethod
    def storage(options):
        sizes = subprocess.run(
            ["du", "-sh", REPOSITORY, DATA_DIR],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        database = subprocess.run(
            ["psql", "-tAc", "SELECT pg_size_pretty(pg_database_size(current_database()))"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        print(sizes)
        print(f"{database or '?'}\tdatabase {os.environ.get('PGDATABASE', '')}")
