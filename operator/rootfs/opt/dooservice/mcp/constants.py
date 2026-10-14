"""The MCP tools' fixed paths, limits and the Odoo shell scripts they run."""

from __future__ import annotations

import os

BRAIN = os.environ.get("DOOSERVICE_BRAIN", "")
#: The most brain facts one search answers with.
BRAIN_MATCHES = 60

MANY_RECORDS = 20
SENSITIVE_PREFIXES = ("account.", "res.users", "res.groups", "ir.rule", "ir.model.access", "res.company")

ODOO_BIN = "/usr/local/bin/odoo-bin"
MARK = "<<dooservice-answer>>"
TIMEOUT_SECONDS = 300
LOG_TAIL = 40
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

READ = """
model = env[request['model']]
domain = request.get('domain') or []
answer['count'] = model.search_count(domain)
records = model.search(domain, limit=request['limit'], order=request.get('order') or None)
answer['records'] = records.read(request.get('fields') or ['display_name'])
"""
COUNT = "answer['count'] = env[request['model']].search_count(request.get('domain') or [])"
WRITE = """
model = env[request['model']]
if request.get('values_list'):
    answer['created'] = model.create(request['values_list']).ids
else:
    records = model.search(request['domain'])
    records.write(request['values'])
    answer['written'] = records.ids
"""
SETTINGS = """
settings = env['res.config.settings']
names = request.get('names') or []
if request.get('values'):
    settings.create(request['values']).execute()
answer['settings'] = {name: settings.default_get([name]).get(name) for name in names or request['values']}
"""
TEXT = {"type": "string"}
DOMAIN = {"type": "array", "description": "An Odoo domain, e.g. [[\"state\", \"=\", \"sale\"]]"}

DOOSERVICE = "/usr/local/bin/dooservice"
REFERENCE = "/opt/dooservice/ai/skills/code/odoo-reference"
ODOO_SOURCE = "/usr/lib/python3/dist-packages/odoo"
TAIL = 60
#: The most lines one search of the code or the reference answers with.
SOURCE_MATCHES = 80

PROTOCOL_VERSION = "2025-06-18"
