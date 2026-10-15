"""What `opencode run --format json` printed, one JSON event a line: its last text and its tokens."""

import json

from dooservice_build import BuildOutcome


class OpencodeEvents:
    def __init__(self, output):
        self.events = []
        for line in output.splitlines():
            try:
                self.events.append(json.loads(line))
            except ValueError:
                continue

    @staticmethod
    def parts(event):
        part = event.get("part") if isinstance(event, dict) else None
        return part if isinstance(part, dict) else {}

    def outcome(self, exited_well, model):
        texts, input_tokens, output_tokens, errors = [], 0, 0, []
        for event in self.events:
            part = self.parts(event)
            if part.get("type") == "text" and part.get("text"):
                texts.append(str(part["text"]))
            tokens = part.get("tokens") if part.get("type") == "step-finish" else None
            if isinstance(tokens, dict):
                cache = tokens.get("cache") if isinstance(tokens.get("cache"), dict) else {}
                input_tokens += int(tokens.get("input") or 0) + int(cache.get("read") or 0) + int(cache.get("write") or 0)
                output_tokens += int(tokens.get("output") or 0) + int(tokens.get("reasoning") or 0)
            if event.get("type") == "error":
                errors.append(self.message(event))
        said = texts[-1] if texts else (errors[-1] if errors else "")
        return BuildOutcome(exited_well and not errors, said, model, input_tokens, output_tokens)

    @staticmethod
    def message(event):
        error = event.get("error") if isinstance(event.get("error"), dict) else {}
        data = error.get("data") if isinstance(error.get("data"), dict) else {}
        return str(data.get("message") or error.get("name") or "opencode failed")
