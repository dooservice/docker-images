"""The dooservice tools for an AI agent in this console, over MCP on stdio.

Reading and changing Odoo goes through the ORM in `odoo-bin shell`, so Odoo's own checks
run; installing, updating and the log go through the `dooservice` command. The agent is
given these first and the terminal second: answers come back trimmed, and what needs the
person's yes, or is not allowed here, is refused with words that say so.

Started as `python3 -m dooservice_mcp`.
"""

from .catalog import TOOLS
from .constants import SERVER_NAME, SERVER_VERSION
from .protocol import McpServer

McpServer(SERVER_NAME, SERVER_VERSION, TOOLS).serve()
