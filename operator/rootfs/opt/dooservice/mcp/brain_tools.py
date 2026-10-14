"""The project's brain, as tools: what production is, read from the files the server keeps.

Mounted read only at `$DOOSERVICE_BRAIN` in a development console. The index comes first
and is short; a fact, a process or the memory is asked for when it is needed.
"""

import json
import os

from constants import BRAIN, BRAIN_MATCHES
from refusal import ToolRefused
from tool import Tool


class BrainFiles:
    @staticmethod
    def path(name):
        if not BRAIN or not os.path.isdir(BRAIN):
            raise ToolRefused("This console has no brain of the project: production has not been read yet.")
        return os.path.join(BRAIN, name)

    @staticmethod
    def json(name):
        try:
            with open(BrainFiles.path(name), encoding="utf-8") as stored:
                return json.load(stored)
        except (OSError, ValueError):
            return {}


class BrainIndex(Tool):
    name = "brain_index"
    description = "What this project's production is: its modules, what the customer added, its processes. Read first."

    def run(self, arguments):
        try:
            with open(BrainFiles.path("index.md"), encoding="utf-8") as index:
                return index.read()
        except OSError as missing:
            raise ToolRefused("The brain has no index yet.") from missing


class BrainFact(Tool):
    name = "brain_fact"
    description = (
        "Facts of production by id (`field:sale.order.x_channel`), by id prefix (`code:`, `automation:`) "
        "or by words in their name."
    )
    schema = {"query": {"type": "string"}}
    required = ("query",)

    def run(self, arguments):
        facts = BrainFiles.json("facts.json").get("facts", {})
        query = arguments["query"].strip()
        if query in facts:
            return self.json({query: facts[query]})
        lowered = query.lower()
        found = {key: fact for key, fact in facts.items()
                 if key.startswith(query) or lowered in str(fact.get("name", "")).lower()}
        shown = dict(list(found.items())[:BRAIN_MATCHES])
        return self.json({"matches": len(found), "facts": shown})


class BrainProcess(Tool):
    name = "brain_process"
    description = "One business process of the project, step by step with the facts each step stands on."
    schema = {"key": {"type": "string"}}
    required = ("key",)

    def run(self, arguments):
        for process in BrainFiles.json("processes.json").get("processes", []):
            if process.get("key") == arguments["key"]:
                return self.json(process)
        raise ToolRefused(f"There is no process {arguments['key']}; brain_index lists them.")


class BrainMemory(Tool):
    name = "brain_memory"
    description = "What was decided and what happened in this project, newest first: deploys, notes, changes made in Odoo."
    schema = {"limit": {"type": "integer"}}

    def run(self, arguments):
        limit = min(int(arguments.get("limit") or 30), 200)
        try:
            with open(BrainFiles.path("memory.jsonl"), encoding="utf-8") as memory:
                lines = memory.read().splitlines()
        except OSError:
            return "The memory is empty."
        return "\n".join(reversed(lines[-limit:]))
