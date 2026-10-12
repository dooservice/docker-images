"""Running a few lines of Python inside Odoo on this environment's database, and reading
back one JSON answer.

Each call starts `odoo-bin shell`, which already carries the database and addons path,
feeds it a script, and keeps only the line the script marks: Odoo's own log goes to
stderr and is shown only when the script never answered. The request travels in an
environment variable, so nothing the agent writes becomes Python source.
"""

import json
import os
import subprocess

from refusal import ToolRefused

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


class OdooShell:
    def run(self, program, request):
        """`program` sets `answer` from `request` and `env`; it is committed only when the
        request says `commit`."""
        environment = {
            **os.environ,
            "DOOSERVICE_REQUEST": json.dumps(request),
            "DOOSERVICE_PROGRAM": program,
            "DOOSERVICE_AI_TOOL": "1",
        }
        try:
            finished = subprocess.run(
                [ODOO_BIN, "shell", "--log-level=warn"], input=SCRIPT, text=True,
                capture_output=True, env=environment, timeout=TIMEOUT_SECONDS, check=False,
            )
        except subprocess.TimeoutExpired as late:
            raise ToolRefused(f"Odoo did not answer within {TIMEOUT_SECONDS} seconds.") from late
        for line in finished.stdout.splitlines():
            if line.startswith(MARK):
                return json.loads(line[len(MARK):])
        tail = "\n".join(finished.stderr.strip().splitlines()[-LOG_TAIL:])
        raise ToolRefused(f"Odoo stopped before answering:\n{tail}")
