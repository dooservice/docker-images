"""Asking the platform for what this container cannot do by itself.

The operator holds no git credentials and cannot touch any container but its own. When
something needs that — restarting Odoo, reading its log, taking the AI slot while an
agent works, publishing what was committed — it asks the agent that started it, over a unix socket the agent created
for this session and nobody else. Which socket it is decides which environment it acts
on, so there is no identifier to forge.

The exchange is one JSON request, then JSON lines back until one says `eof`:

    → {"action": "restart", "args": {}}
    ← {"rc": 0, "eof": false, "payload": "Restarting dev…"}
    ← {"rc": 0, "eof": true, "payload": ""}
"""

import json
import os
import socket
import sys

from dooservice_constants import SOCKET_PATH, TIMEOUT_SECONDS


class ControlError(Exception):
    def __init__(self, rc, message):
        super().__init__(message)
        self.rc = rc


class ControlClient:
    def __init__(self, path=SOCKET_PATH, timeout=TIMEOUT_SECONDS):
        self.path = path
        self.timeout = timeout

    def ask(self, action, args=None):
        """Every payload the agent sends back, as it arrives. Raises on a non-zero `rc`."""
        if not os.path.exists(self.path):
            raise ControlError(69, "this session has no connection to the platform")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(self.timeout)
            connection.connect(self.path)
            connection.sendall(json.dumps({"action": action, "args": args or {}}).encode() + b"\n")
            buffer = b""
            while True:
                chunk = connection.recv(65536)
                if not chunk:
                    raise ControlError(70, "the platform closed the connection before answering")
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    answer = json.loads(line)
                    if answer.get("rc", 0) != 0:
                        raise ControlError(answer["rc"], answer.get("payload") or "the platform refused")
                    if answer.get("payload"):
                        yield answer["payload"]
                    if answer.get("eof"):
                        return

    def run(self, action, args=None):
        """Print every payload and exit with the platform's answer, the way a command should."""
        try:
            for payload in self.ask(action, args):
                sys.stdout.write(f"{payload}\n")
                sys.stdout.flush()
        except ControlError as error:
            sys.stderr.write(f"{error}\n")
            sys.exit(error.rc)
        except (OSError, TimeoutError) as error:
            sys.stderr.write(f"could not reach the platform: {error}\n")
            sys.exit(75)
        sys.exit(0)
