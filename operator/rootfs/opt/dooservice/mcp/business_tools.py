"""The business layer, as tools: what production is, read from the files the server keeps.

Mounted read only at `$DOOSERVICE_BUSINESS` in a development console. The index comes
first and is short; an area, a fact or what changed is asked for when it is needed. The
process forms and the tickets live in the Dooservice panel, not here: the console only
sees the reading of production.
"""

import json
import os

from constants import BUSINESS, BUSINESS_MATCHES
from refusal import ToolRefused
from tool import Tool


class BusinessFiles:
    @staticmethod
    def path(name):
        if not BUSINESS or not os.path.isdir(BUSINESS):
            raise ToolRefused("This console has no reading of production: it has not been read yet.")
        return os.path.join(BUSINESS, name)

    @staticmethod
    def json(name):
        try:
            with open(BusinessFiles.path(name), encoding="utf-8") as stored:
                return json.load(stored)
        except (OSError, ValueError):
            return {}


class BusinessIndex(Tool):
    name = "business_index"
    description = (
        "What this project's production is: each area's usage and configuration, what was made outside a "
        "module, and when it was read. Read first."
    )

    def run(self, arguments):
        try:
            with open(BusinessFiles.path("index.md"), encoding="utf-8") as index:
                return index.read()
        except OSError as missing:
            raise ToolRefused("The reading has no index yet.") from missing


class BusinessFact(Tool):
    name = "business_fact"
    description = (
        "Facts of production by id (`field:sale.order.x_channel`), by id prefix (`module:`, `code:`, "
        "`automation:`) or by words in their name."
    )
    schema = {"query": {"type": "string"}}
    required = ("query",)

    def run(self, arguments):
        facts = BusinessFiles.json("facts.json").get("facts", {})
        query = arguments["query"].strip()
        if query in facts:
            return self.json({query: facts[query]})
        lowered = query.lower()
        found = {key: fact for key, fact in facts.items()
                 if key.startswith(query) or lowered in str(fact.get("name", "")).lower()}
        shown = dict(list(found.items())[:BUSINESS_MATCHES])
        return self.json({"matches": len(found), "facts": shown})


class BusinessArea(Tool):
    name = "business_area"
    description = (
        "One area of production as it was read (`sales`, `accounting`, ...): its records, what it uses and "
        "its configuration with where each setting comes from. Without an area, the reading's summary: "
        "version, modules, users, what could not be read and how the last reading differs."
    )
    schema = {"area": {"type": "string"}}

    def run(self, arguments):
        reading = BusinessFiles.json("reading.json")
        if not reading:
            raise ToolRefused("Production has not been read yet.")
        area = str(arguments.get("area") or "").strip()
        if not area:
            summary = {key: value for key, value in reading.items() if key not in ("areas", "outside", "models")}
            summary["areas"] = [item.get("area") for item in reading.get("areas", [])]
            return self.json(summary)
        for item in reading.get("areas", []):
            if item.get("area") == area:
                return self.json(item)
        if area == "outside":
            return self.json({"outside": reading.get("outside", [])})
        raise ToolRefused(f"There is no area {area}; business_area without an area lists them.")


class BusinessChanges(Tool):
    name = "business_changes"
    description = (
        "What changed in production between the last two readings: the facts added, removed and changed, "
        "with their names. Row counts are not changes."
    )

    def run(self, arguments):
        changes = BusinessFiles.json("changes.json")
        if not changes:
            return "There is no earlier reading to compare with."
        return self.json(changes)
