"""What a console on production may do right now.

A console on production connects as a database role of its own that can only read, so
the database refuses any write whatever tool tries it. It opens making a backup, and once
the backup is ready the agent leaves the environment's own credentials, and until when
they count, in the session's control directory, which this container can read and not
write. From then on the person's `psql` and `odoo-bin` write with them, and the AI's
`odoo-bin` — its Odoo shell and its ORM tools —; the AI's `psql` never does.
"""

import json
import os
import time

from dooservice_constants import CHANGES_UNTIL, READ_ONLY, WRITE_CREDENTIALS


class Production:
    @staticmethod
    def here():
        return os.environ.get("DOOSERVICE_STAGE") == "production"

    @staticmethod
    def changes_allowed():
        if not Production.here():
            return True
        try:
            with open(CHANGES_UNTIL) as stored:
                return float(stored.read().strip() or 0) > time.time()
        except (OSError, ValueError):
            return False

    @staticmethod
    def environment(writes):
        """This process's environment, read-write only when it may write and the backup is ready."""
        environment = dict(os.environ)
        if not (Production.here() and writes):
            return environment
        credentials = Production.write_credentials()
        if credentials is not None:
            environment["PGUSER"], environment["PGPASSWORD"] = credentials
            environment["PGOPTIONS"] = environment.get("PGOPTIONS", "").replace(READ_ONLY, "").strip()
        return environment

    @staticmethod
    def write_credentials():
        """The environment's user and password, once the backup is ready; else nothing."""
        try:
            with open(WRITE_CREDENTIALS) as stored:
                credentials = json.load(stored)
        except (OSError, ValueError):
            return None
        if float(credentials.get("until", 0)) <= time.time():
            return None
        return credentials["user"], credentials["password"]

    @staticmethod
    def refuse(what):
        """Nothing that a deploy does is done from a production console."""
        if Production.here():
            raise SystemExit(f"{what} is not done from a production console: it goes through a deploy.")

    @staticmethod
    def require_changes(what):
        if Production.here() and not Production.changes_allowed():
            raise SystemExit(f"{what} on production waits for the backup this session made as it opened.")
