"""The tests run in this session, kept so a pull request can list them.

`dooservice test` runs the tests as a child and records each run here: which modules,
whether they passed, when (UTC) and how long it took. The file is in the session's home,
so it goes with the session; `dooservice publish` sends every run it holds.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import time

from .constants import TEST_RUNS


class TestRuns:
    """This session's test runs, one JSON line each."""

    def __init__(self, path=TEST_RUNS):
        self.path = os.path.expanduser(path)

    def run(self, modules, command):
        """Run the tests, record the run, and return their exit code."""
        moment = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        started = time.monotonic()
        code = subprocess.run(command, check=False).returncode
        self.record(
            {
                "modules": modules,
                "passed": code == 0,
                "at": moment,
                "seconds": round(time.monotonic() - started),
            }
        )
        return code

    def record(self, run):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a") as runs:
            runs.write(json.dumps(run) + "\n")

    def all(self):
        """Every run recorded, oldest first; a line that cannot be read is skipped."""
        try:
            with open(self.path) as runs:
                lines = runs.read().splitlines()
        except OSError:
            return []
        recorded = []
        for line in lines:
            try:
                recorded.append(json.loads(line))
            except ValueError:
                continue
        return recorded
