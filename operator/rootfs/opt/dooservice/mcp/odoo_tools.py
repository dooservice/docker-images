"""Reading and changing Odoo records and settings through the ORM, as tools."""

from constants import COUNT, DOMAIN, READ, SETTINGS, TEXT, WRITE
from gate import Gate
from odoo_shell import OdooShell
from tool import Tool

shell, gate = OdooShell(), Gate()


class OdooRead(Tool):
    name = "odoo_read"
    description = "Read records of an Odoo model: how many match, and the first ones with the fields asked for."
    schema = {"model": TEXT, "domain": DOMAIN, "fields": {"type": "array", "items": TEXT},
              "limit": {"type": "integer"}, "order": TEXT}
    required = ("model",)

    def run(self, arguments):
        request = {**arguments, "limit": min(int(arguments.get("limit") or 20), 200)}
        return self.json(shell.run(READ, request))


class OdooWrite(Tool):
    name = "odoo_write"
    description = (
        "Create records (values_list) or write values on the records a domain matches, through the ORM. "
        "Many records, access rights, accounting and users need confirmed=true after the user said yes."
    )
    schema = {"model": TEXT, "domain": DOMAIN, "values": {"type": "object"},
              "values_list": {"type": "array", "items": {"type": "object"}}, "confirmed": {"type": "boolean"}}
    required = ("model",)

    def run(self, arguments):
        gate.ensure_changes_allowed()
        model = arguments["model"]
        count = len(arguments.get("values_list") or []) or shell.run(COUNT, arguments)["count"]
        gate.ensure_confirmed(model, count, bool(arguments.get("confirmed")))
        return self.json(shell.run(WRITE, {**arguments, "commit": True}))


class OdooSettings(Tool):
    name = "odoo_settings"
    description = (
        "Read Settings fields (names), or change them (values) the way the Settings screen does, so their "
        "side effects run. Field names are in the odoo-reference skill, settings.md."
    )
    schema = {"names": {"type": "array", "items": TEXT}, "values": {"type": "object"}, "confirmed": {"type": "boolean"}}
    required = ()

    def run(self, arguments):
        if arguments.get("values"):
            gate.ensure_changes_allowed()
            gate.ensure_confirmed("res.config.settings", len(arguments["values"]), bool(arguments.get("confirmed")))
        return self.json(shell.run(SETTINGS, {**arguments, "commit": bool(arguments.get("values"))}))
