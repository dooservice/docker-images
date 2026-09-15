"""Prepare, once at build time, what opencode installs for its plugins on first start.

opencode installs `@opencode-ai/plugin` with npm the first time it finds a plugin in its
config directory, and every console starts with an empty home: that was ten seconds of a
blank screen at the start of every session. It is run here once, with the rtk plugin in
place, and the resulting directory is kept for the launcher to copy into each session.
"""

import os
import pty
import select
import shutil
import subprocess
import sys
import time

HOME = "/tmp/opencode-template-home"
TEMPLATE = "/opt/dooservice/opencode-config"
READY = b"all LSPs are disabled"
TIMEOUT_SECONDS = 180

os.makedirs(HOME, exist_ok=True)
os.environ["HOME"] = HOME
subprocess.run(["rtk", "init", "-g", "--opencode"], input="n\n", text=True, capture_output=True, check=True)

pid, descriptor = pty.fork()
if pid == 0:
    os.environ["OPENCODE_CONFIG"] = "/opt/dooservice/ai/opencode.json"
    os.execv("/opt/ai/opencode", ["/opt/ai/opencode", "--print-logs", HOME])

output = b""
started = time.time()
while time.time() - started < TIMEOUT_SECONDS and READY not in output:
    readable, _, _ = select.select([descriptor], [], [], 1)
    if readable:
        try:
            output += os.read(descriptor, 65536)
        except OSError:
            break
os.kill(pid, 9)
os.waitpid(pid, 0)

config = os.path.join(HOME, ".config", "opencode")
if READY not in output or not os.path.isdir(os.path.join(config, "node_modules")):
    sys.stderr.write("opencode did not install its plugin dependencies\n")
    sys.exit(1)
shutil.copytree(config, TEMPLATE, symlinks=True)
shutil.rmtree(HOME)
