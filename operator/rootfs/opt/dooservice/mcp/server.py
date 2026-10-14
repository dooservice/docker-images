"""The dooservice tools for an AI agent in this console, over MCP on stdio.

Reading and changing Odoo goes through the ORM in `odoo-bin shell`, so Odoo's own checks
run; installing, updating and the log go through the `dooservice` command. The agent is
given these first and the terminal second: answers come back trimmed, and what needs the
person's yes, or is not allowed here, is refused with words that say so.
"""

import sys

sys.path.insert(0, "/opt/dooservice/mcp")

from catalog import TOOLS  # noqa: E402
from protocol import McpServer  # noqa: E402

McpServer("dooservice", "1.0.0", TOOLS).serve()
