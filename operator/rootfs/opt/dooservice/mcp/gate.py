"""Whether this session may change anything, and what needs the person's yes first.

A development environment may be changed; production only while its console has changes
allowed, which the platform says by writing until when in the session's control
directory. Some changes always need the person: many records at once, access rights,
accounting, users. The tool refuses them once with what it would do, and the agent comes
back with `confirmed` after asking.
"""

import os
import time

from protocol import ToolRefused

CONTROL_DIR = os.path.dirname(os.environ.get("DOOSERVICE_CONTROL_SOCKET", "/run/dooservice/control.sock"))
CHANGES_UNTIL = os.path.join(CONTROL_DIR, "changes-until")
MANY_RECORDS = 20
SENSITIVE_PREFIXES = ("account.", "res.users", "res.groups", "ir.rule", "ir.model.access", "res.company")


class Gate:
    @staticmethod
    def production():
        return os.environ.get("DOOSERVICE_STAGE") == "production"

    def ensure_changes_allowed(self):
        if not self.production():
            return
        try:
            with open(CHANGES_UNTIL) as stored:
                until = float(stored.read().strip() or 0)
        except (OSError, ValueError):
            until = 0
        if until < time.time():
            raise ToolRefused(
                "This is production and changes are not allowed in this session. Explain the change to the "
                "user; they can press «Allow changes» in the panel, and then you can make it."
            )

    def ensure_confirmed(self, model, count, confirmed):
        if confirmed:
            return
        if count > MANY_RECORDS or model.startswith(SENSITIVE_PREFIXES):
            raise ToolRefused(
                f"This changes {count} record(s) of {model}. Tell the user what will change, on which records "
                "and how to undo it, and call again with confirmed=true only after they say yes."
            )

    def ensure_modules_allowed(self):
        if self.production():
            raise ToolRefused("Modules are not installed or updated from a production console: that is a deploy.")
