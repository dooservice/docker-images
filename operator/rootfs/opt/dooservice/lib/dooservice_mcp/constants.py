"""The MCP tools' fixed paths, limits and the Odoo shell scripts they run."""

from __future__ import annotations

from dooservice_console.constants import SKILLS_DIR

#: The name the server gives itself to the client.
SERVER_NAME = "dooservice"
#: The version the server gives itself to the client.
SERVER_VERSION = "1.0.0"
#: The MCP version answered when the client names none.
PROTOCOL_VERSION = "2025-06-18"
#: JSON-RPC's code for a method the server does not know.
UNKNOWN_METHOD = -32601

#: More records than this at once need the person's yes.
MANY_RECORDS = 20
#: Models whose changes always need the person's yes.
SENSITIVE_PREFIXES = ("account.", "res.users", "res.groups", "ir.rule", "ir.model.access", "res.company")

#: The generated reference of this Odoo version.
REFERENCE = f"{SKILLS_DIR}/code/odoo-reference"
#: What starts the one line of the shell's output that carries the answer.
MARK = "<<dooservice-answer>>"
#: How long one Odoo shell call may take.
TIMEOUT_SECONDS = 300
#: How long a module install or update may take.
COMMAND_TIMEOUT_SECONDS = 900
#: How long reading the log may take.
LOGS_TIMEOUT_SECONDS = 60
#: The lines of Odoo's log shown when the shell never answered.
LOG_TAIL = 40
#: The lines of a command's output an agent is shown.
TAIL = 60
#: The most lines one search of the code or the reference answers with.
SOURCE_MATCHES = 80
#: The most characters of each line a search answers with.
MATCH_WIDTH = 240
#: The records `odoo_read` returns when no limit is asked for.
READ_LIMIT = 20
#: The most records `odoo_read` returns.
READ_MAXIMUM = 200
#: The log lines `odoo_logs` returns when no number is asked for.
LOG_LINES = 200
#: The most log lines `odoo_logs` returns.
LOG_LINES_MAXIMUM = 1000

#: The script fed to the Odoo shell: it runs the tool's program on the request and prints the answer.
SCRIPT = f"""
import json, os
request = json.loads(os.environ['DOOSERVICE_REQUEST'])
answer = {{}}
exec(compile(os.environ['DOOSERVICE_PROGRAM'], 'dooservice-tool', 'exec'))
if request.get('commit'):
    env.cr.commit()
else:
    env.cr.rollback()
print({MARK!r} + json.dumps(answer, default=str))
"""
#: Counts the records a domain matches and reads the first ones.
READ = """
model = env[request['model']]
domain = request.get('domain') or []
answer['count'] = model.search_count(domain)
records = model.search(domain, limit=request['limit'], order=request.get('order') or None)
answer['records'] = records.read(request.get('fields') or ['display_name'])
"""
#: Counts the records a domain matches.
COUNT = "answer['count'] = env[request['model']].search_count(request.get('domain') or [])"
#: Creates records, or writes values on the records a domain matches.
WRITE = """
model = env[request['model']]
if request.get('values_list'):
    answer['created'] = model.create(request['values_list']).ids
else:
    records = model.search(request['domain'])
    records.write(request['values'])
    answer['written'] = records.ids
"""
#: Reads Settings fields, or changes them the way the Settings screen does.
SETTINGS = """
settings = env['res.config.settings']
names = request.get('names') or []
if request.get('values'):
    settings.create(request['values']).execute()
answer['settings'] = {name: settings.default_get([name]).get(name) for name in names or request['values']}
"""
#: A text argument of a tool.
TEXT = {"type": "string"}
#: An Odoo domain argument of a tool.
DOMAIN = {"type": "array", "description": "An Odoo domain, e.g. [[\"state\", \"=\", \"sale\"]]"}
