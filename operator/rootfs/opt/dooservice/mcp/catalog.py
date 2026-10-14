"""Every tool this console's MCP server offers, in the order an agent sees them."""

from brain_tools import BrainFact, BrainIndex, BrainMemory, BrainProcess
from odoo_tools import OdooRead, OdooSettings, OdooWrite
from platform_tools import ModuleInstall, ModuleUpdate, OdooFind, OdooLogs

TOOLS = (
    OdooRead(), OdooWrite(), OdooSettings(), ModuleInstall(), ModuleUpdate(), OdooLogs(), OdooFind(),
    BrainIndex(), BrainFact(), BrainProcess(), BrainMemory(),
)
