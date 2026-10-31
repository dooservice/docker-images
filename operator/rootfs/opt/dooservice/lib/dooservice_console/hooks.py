"""Every git hook of the console, and the repository's own after it.

The console points `core.hooksPath` at /opt/dooservice/git-hooks for every repository, so
git looks for its hooks there and no longer in the repository's. Each hook name is a link
to one entry point, which does the console's part and then runs the repository's hook of
that name, if it has one, with the same arguments and input: a repository keeps its hooks.

The console's part is one line: a commit written by an AI tool of the console is
co-authored by Dooservice, the way a commit written by Claude Code is by Claude. The
trailer is git's own word, so it is in English whatever the person's language, and it is
added once however often the message is edited.
"""

from __future__ import annotations

import os
import subprocess

from .constants import CO_AUTHOR, PREPARE_COMMIT_MSG, SESSION_MARK


class Hook:
    """The hook git ran, by the name it was called with."""

    def __init__(self, argv):
        self.entry = argv[0]
        self.name = os.path.basename(argv[0])
        self.args = argv[1:]

    def run(self):
        if self.name == PREPARE_COMMIT_MSG and os.environ.get(SESSION_MARK):
            self.co_author()
        repository_hook = self.repository_hook()
        if repository_hook:
            os.execv(repository_hook, [repository_hook, *self.args])
        return 0

    def co_author(self):
        message_file = self.args[0] if self.args else ""
        if not message_file:
            return
        subprocess.run(
            ["git", "interpret-trailers", "--in-place", "--if-exists", "addIfDifferent", "--trailer", CO_AUTHOR,
             message_file],
            check=False,
        )

    def repository_hook(self):
        """The repository's hook of this name, where git would have run it without us.

        Asked of the common git directory and not with `--git-path hooks/…`, which follows
        `core.hooksPath` back here and would run this hook again for ever.
        """
        found = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=False,
        )
        common = found.stdout.strip()
        if found.returncode != 0 or not common:
            return ""
        path = os.path.join(common, "hooks", self.name)
        if os.path.realpath(path) == os.path.realpath(self.entry):
            return ""
        return path if os.path.isfile(path) and os.access(path, os.X_OK) else ""
