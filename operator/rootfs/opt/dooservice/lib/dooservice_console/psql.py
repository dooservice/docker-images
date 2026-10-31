"""`psql` on this environment's database: read only for an AI session, on development
and on production alike.

The agent changes data through the ORM, which runs Odoo's own checks and computes; `psql`
is there to read and diagnose. The AI launcher marks its session with
`DOOSERVICE_AI_SESSION`, and every `psql` the agent starts opens its transactions read
only. A person at the console's own shell writes on development, and on production once
the backup the session made as it opened is ready (`production`).
"""

from __future__ import annotations

import os

from .constants import READ_ONLY, REAL_PSQL, SESSION_MARK
from .production import Production


class PsqlCommand:
    """PostgreSQL's own `psql`, with the connection this caller may have."""

    def __init__(self, args):
        self.args = list(args)

    def run(self):
        agent = bool(os.environ.get(SESSION_MARK))
        environment = Production.environment(writes=not agent)
        if agent and READ_ONLY not in environment.get("PGOPTIONS", ""):
            environment["PGOPTIONS"] = f"{environment.get('PGOPTIONS', '')} {READ_ONLY}".strip()
        os.execve(REAL_PSQL, [REAL_PSQL, *self.args], environment)
