"""Claude Code and opencode, each run once without a prompt to answer, and what they report back."""

import json
import os
import subprocess
import tempfile

from dooservice_build import BuildOutcome, BuildTask
from dooservice_build_events import OpencodeEvents
from dooservice_constants import (
    AI_DIR,
    BUILD_ODOO_SOURCE,
    BUILD_PLATFORM_ADDONS,
    COMPATIBLE_PACKAGE,
    COMPATIBLE_PROVIDER,
    REPOSITORY,
)



class ClaudeBuild:
    def run(self, task: BuildTask):
        environment = task.child_environment("ANTHROPIC_API_KEY")
        if task.base_url:
            environment["ANTHROPIC_BASE_URL"] = task.base_url
        if task.max_output_tokens:
            environment["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(task.max_output_tokens)
        claude_dir = os.path.join(environment["HOME"], ".claude")
        os.makedirs(claude_dir, exist_ok=True)
        with open(os.path.join(claude_dir, "CLAUDE.md"), "w") as memory:
            memory.write(f"@{task.instructions()}\n")
        command = [
            "/opt/ai/claude", "-p", task.prompt, "--output-format", "json", "--model", task.model,
            f"--settings={AI_DIR}/settings-build.json", "--strict-mcp-config", "--no-session-persistence",
            f"--add-dir={AI_DIR}/", f"--add-dir={BUILD_ODOO_SOURCE}", f"--add-dir={BUILD_PLATFORM_ADDONS}",
            f"--append-system-prompt={task.rules()}",
        ]
        done = subprocess.run(command, cwd=REPOSITORY, env=environment, capture_output=True, text=True)
        try:
            report = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return BuildOutcome(False, done.stderr.strip()[-500:], task.model, 0, 0)
        usage = report.get("usage") or {}
        spent = sum(int(usage.get(name) or 0) for name in
                    ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        model = next(iter(report.get("modelUsage") or {}), task.model)
        finished = done.returncode == 0 and not report.get("is_error")
        return BuildOutcome(finished, str(report.get("result") or ""), model, spent, int(usage.get("output_tokens") or 0))


class OpencodeBuild:
    def config(self, task: BuildTask):
        with open(f"{AI_DIR}/opencode-build.json") as managed:
            config = json.load(managed)
        limit = {"limit": {"output": task.max_output_tokens}} if task.max_output_tokens else {}
        if task.provider == "openai_compatible":
            options = {"baseURL": task.base_url, "apiKey": "{env:OPENAI_API_KEY}"}
            provider = {"npm": COMPATIBLE_PACKAGE, "options": options, "models": {task.model: limit}}
            config["provider"] = {COMPATIBLE_PROVIDER: provider}
            return config, f"{COMPATIBLE_PROVIDER}/{task.model}"
        config["provider"] = {"openai": {"models": {task.model: limit}}}
        return config, f"openai/{task.model}"

    def run(self, task: BuildTask):
        environment = task.child_environment("OPENAI_API_KEY")
        config, model = self.config(task)
        config["instructions"] = [task.instructions()]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as written:
            json.dump(config, written)
        environment["OPENCODE_CONFIG"] = written.name
        command = ["/opt/ai/opencode", "run", "--format", "json", "--model", model, "--dir", REPOSITORY,
                   f"{task.rules()}\n\n{task.prompt}"]
        try:
            done = subprocess.run(command, cwd=REPOSITORY, env=environment, capture_output=True, text=True)
        finally:
            os.unlink(written.name)
        return OpencodeEvents(done.stdout).outcome(done.returncode == 0, task.model)
