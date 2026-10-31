"""What the image prepares once, at build time, so each session starts ready.

The AI tools' settings are merged from their layers (`settings`). Then opencode: it
installs `@opencode-ai/plugin` with npm the first time it finds a plugin in its config
directory, and every console starts with an empty home: that was ten seconds of a blank
screen at the start of every session. It is run here once, with the rtk plugin in place,
and the resulting directory is kept for the launcher to copy into each session.

Run as `python3 -m dooservice_console.build` from the Dockerfile.
"""

from __future__ import annotations

import os
import pty
import select
import shutil
import signal
import subprocess
import sys
import time

from .constants import (
    DEVELOPMENT,
    OPENCODE_BINARY,
    OPENCODE_CONFIG_VARIABLE,
    PLUGINS_BUILD_HOME,
    PLUGINS_READY,
    PLUGINS_TEMPLATE,
    PLUGINS_TIMEOUT_SECONDS,
    READ_BYTES,
    SETTINGS_FILES,
)
from .settings import SettingsLayers


class OpencodePlugins:
    """opencode run once in a throwaway home until its plugins are installed, then kept."""

    def prepare(self):
        os.makedirs(PLUGINS_BUILD_HOME, exist_ok=True)
        os.environ["HOME"] = PLUGINS_BUILD_HOME
        subprocess.run(["rtk", "init", "-g", "--opencode"], input="n\n", text=True, capture_output=True, check=True)
        output = self.run_opencode()
        config = os.path.join(PLUGINS_BUILD_HOME, ".config", "opencode")
        if PLUGINS_READY not in output or not os.path.isdir(os.path.join(config, "node_modules")):
            sys.stderr.write("opencode did not install its plugin dependencies\n")
            sys.exit(1)
        shutil.copytree(config, PLUGINS_TEMPLATE, symlinks=True)
        shutil.rmtree(PLUGINS_BUILD_HOME)

    @staticmethod
    def run_opencode():
        """What opencode prints until it says it is ready, or the time is up."""
        child, descriptor = pty.fork()
        if child == 0:
            os.environ[OPENCODE_CONFIG_VARIABLE] = SETTINGS_FILES["opencode"][DEVELOPMENT]
            os.execv(OPENCODE_BINARY, [OPENCODE_BINARY, "--print-logs", PLUGINS_BUILD_HOME])
        output = b""
        started = time.time()
        while time.time() - started < PLUGINS_TIMEOUT_SECONDS and PLUGINS_READY not in output:
            if select.select([descriptor], [], [], 1)[0]:
                try:
                    output += os.read(descriptor, READ_BYTES)
                except OSError:
                    break
        os.kill(child, signal.SIGKILL)
        os.waitpid(child, 0)
        return output


if __name__ == "__main__":
    SettingsLayers().write()
    OpencodePlugins().prepare()
