"""The Model Context Protocol over stdio, as much of it as a server of tools needs.

One JSON-RPC message per line in each direction. The client says `initialize`, asks for
`tools/list`, then calls `tools/call` as often as it likes; notifications get no answer.
A tool that fails answers with `isError`, so the agent reads why instead of the session
seeing a protocol error.
"""

import json
import sys

from refusal import ToolRefused

PROTOCOL_VERSION = "2025-06-18"


class McpServer:
    def __init__(self, name, version, tools):
        self.name = name
        self.version = version
        self.tools = {tool.name: tool for tool in tools}

    def serve(self):
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                message = json.loads(line)
            except ValueError:
                continue
            answer = self.answer(message)
            if answer is not None and "id" in message:
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message["id"], **answer}) + "\n")
                sys.stdout.flush()

    def answer(self, message):
        method = message.get("method", "")
        params = message.get("params") or {}
        if method == "initialize":
            return {"result": {
                "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            }}
        if method == "tools/list":
            return {"result": {"tools": [tool.describe() for tool in self.tools.values()]}}
        if method == "tools/call":
            return {"result": self.call(params.get("name", ""), params.get("arguments") or {})}
        if method == "ping":
            return {"result": {}}
        if method.startswith("notifications/"):
            return None
        return {"error": {"code": -32601, "message": f"unknown method {method}"}}

    def call(self, name, arguments):
        tool = self.tools.get(name)
        if tool is None:
            return self.text(f"There is no tool called {name}.", failed=True)
        try:
            return self.text(tool.run(arguments))
        except ToolRefused as refused:
            return self.text(str(refused), failed=True)

    @staticmethod
    def text(content, failed=False):
        return {"content": [{"type": "text", "text": content}], "isError": failed}
