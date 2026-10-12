"""What a console on production may do right now.

A console on production connects as a database role of its own that can only read, so
the database refuses any write whatever tool tries it. While its changes are allowed —
after a backup — the agent leaves the environment's own credentials, and until when they
count, in the session's control directory, which this container can read and not write;
the console's tools then connect with them. The AI's `psql` never does: it changes data
through the ORM tools, which ask before anything wide.
"""

import json
import os
import time

CONTROL_DIR = os.path.dirname(os.environ.get("DOOSERVICE_CONTROL_SOCKET", "/run/dooservice/control.sock"))
CHANGES_UNTIL = os.path.join(CONTROL_DIR, "changes-until")
WRITE_CREDENTIALS = os.path.join(CONTROL_DIR, "write-credentials")
READ_ONLY = "-c default_transaction_read_only=on"


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
    def through_tools():
        """Whether this is the AI's own ORM tools, which ask before anything wide; the AI
        anywhere else on production only reads."""
        ai = bool(os.environ.get("DOOSERVICE_AI_SESSION"))
        return not ai or bool(os.environ.get("DOOSERVICE_AI_TOOL"))

    @staticmethod
    def environment(writes):
        """This process's environment, read-write only when it may write and changes are allowed."""
        environment = dict(os.environ)
        if not (Production.here() and writes and Production.through_tools()):
            return environment
        credentials = Production.write_credentials()
        if credentials is not None:
            environment["PGUSER"], environment["PGPASSWORD"] = credentials
            environment["PGOPTIONS"] = environment.get("PGOPTIONS", "").replace(READ_ONLY, "").strip()
        return environment

    @staticmethod
    def write_credentials():
        """The environment's user and password, while changes are allowed; else nothing."""
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
            raise SystemExit(f"{what} on production needs changes allowed: press «Allow changes» in the panel.")
