"""`odoo` with this environment's database already wired in.

The same idea as the wrapper on odoo.sh: whoever calls it — a person or an agent — never
passes the database, its host or the addons path, and cannot point it at another
database by mistake. The password is not on the command line: libpq reads PGPASSWORD
from the environment, so it never shows up in `ps`.

No HTTP by default. This container is not the one serving the environment; it only
installs, updates, tests and opens shells against the same database.

Without a repository, no other addons path is accepted: a module installed from anywhere
else would be in the database and missing from the environment's Odoo, which would then
fail to load it.
"""

from __future__ import annotations

import os
import sys

from .constants import (
    ADDONS_PATH_VARIABLE,
    DATA_DIR,
    DATABASE_COMMANDS,
    DEFAULT_DATABASE_PORT,
    DEFAULT_MAXCONN,
    MODULE_OPTION_PREFIXES,
    MODULE_OPTIONS,
    REAL_ODOO,
    REPOSITORY,
)
from .production import Production


class OdooCommand:
    """Odoo's own command, with the environment's database options added to what was asked."""

    def __init__(self, args):
        self.args = list(args)

    def run(self):
        if not os.path.isdir(os.path.join(REPOSITORY, ".git")) and any(
            argument.startswith("--addons-path") for argument in self.args
        ):
            sys.stderr.write(
                "This project has no repository: only the modules the environment already has can be installed.\n"
                "Link a repository to the project to develop modules of its own.\n"
            )
            sys.exit(2)
        if any(argument in MODULE_OPTIONS or argument.startswith(MODULE_OPTION_PREFIXES) for argument in self.args):
            Production.refuse("Installing or updating modules")
        os.environ.update(Production.environment(writes=True))
        command = self.args[0] if self.args and not self.args[0].startswith("-") else None
        rest = self.args[1:] if command else self.args
        os.execv(REAL_ODOO, [REAL_ODOO, *self.arguments(command, rest)])

    @staticmethod
    def arguments(command, args):
        """The command, the addons path, what was asked, then the database options it needs."""
        injected = []
        if command is None or command in DATABASE_COMMANDS:
            database = os.environ["PGDATABASE"]
            injected = [
                "--db_host", os.environ["PGHOST"],
                "--db_port", os.environ.get("PGPORT", DEFAULT_DATABASE_PORT),
                "--db_user", os.environ["PGUSER"],
                "--database", database,
                f"--db-filter=^{database}$",
                "--no-database-list",
                "--data-dir", DATA_DIR,
                "--workers=0",
            ]
            if not any(argument.startswith("--db_maxconn") for argument in args):
                injected.append(DEFAULT_MAXCONN)
            if not any(argument.startswith(("--http-port", "--http-interface")) for argument in args):
                injected.append("--no-http")
        addons_path = os.environ.get(ADDONS_PATH_VARIABLE)
        base = [f"--addons-path={addons_path}"] if addons_path else []
        leading = [command] if command else []
        return leading + base + args + injected
