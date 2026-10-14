"""Whether this session may change anything, and what needs the person's yes first.

A development environment may be changed; production once the backup its console made
as it opened is ready, which the platform says by writing until when in the session's
control directory. Some changes always need the person: many records at once, access rights,
accounting, users. The tool refuses them once with what it would do, and the agent comes
back with `confirmed` after asking.
"""

from constants import MANY_RECORDS, SENSITIVE_PREFIXES
from dooservice_production import Production
from refusal import ToolRefused


class Gate:
    @staticmethod
    def production():
        return Production.here()

    def ensure_changes_allowed(self):
        if not Production.changes_allowed():
            raise ToolRefused(
                "This is production and the backup this session made as it opened is not ready yet, so nothing "
                "can change. Tell the user, and try again in a few minutes."
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
