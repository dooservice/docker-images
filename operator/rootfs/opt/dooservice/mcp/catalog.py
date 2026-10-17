"""Every tool this console's MCP server offers, in the order an agent sees them."""

from odoo_tools import OdooRead, OdooSettings, OdooWrite
from platform_tools import ModuleInstall, ModuleUpdate, OdooFind, OdooLogs

TOOLS = (
    OdooRead(), OdooWrite(), OdooSettings(), ModuleInstall(), ModuleUpdate(), OdooLogs(), OdooFind(),
)
