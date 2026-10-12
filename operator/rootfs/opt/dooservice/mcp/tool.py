"""One tool the agent can call: its name, what it does, what it takes, and how it runs."""

import json


class Tool:
    name = ""
    description = ""
    schema: dict = {}
    required: tuple = ()

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {"type": "object", "properties": self.schema, "required": list(self.required)},
        }

    def run(self, arguments):
        raise NotImplementedError

    @staticmethod
    def json(answer):
        return json.dumps(answer, ensure_ascii=False, indent=1, default=str)
