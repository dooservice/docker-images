"""One request built as a module, with no one at the keyboard: what the agent asked, and who builds it.

The agent starts this in a console of a development environment whose database is a
scratch one, with no records. The key arrives in this process's environment only; the
tool gets it under the name it reads, and nothing writes it anywhere.
"""

import json
import os

from dooservice_constants import (
    AI_DIR,
    BUILD_KEPT_OUT,
    BUILD_MODULE_CHARACTERS,
    BUILD_PROVIDERS,
    BUILD_REQUIRED,
    PRODUCTION,
    REPOSITORY,
)


class BuildError(Exception):
    """Why the build did not start, in a sentence for the agent's log."""


class BuildOutcome:
    def __init__(self, finished, changes, model, input_tokens, output_tokens):
        self.finished = finished
        self.changes = changes
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def line(self):
        return json.dumps({"changes": self.changes, "model": self.model, "input_tokens": self.input_tokens,
                           "output_tokens": self.output_tokens}, ensure_ascii=False)


class BuildTask:
    def __init__(self, environ=None):
        environ = os.environ if environ is None else environ
        missing = [name for name in BUILD_REQUIRED if not environ.get(name)]
        if missing:
            raise BuildError(f"missing {', '.join(missing)}")
        if environ.get("DOOSERVICE_STAGE") == PRODUCTION:
            raise BuildError("a request is never built on production")
        self.provider = environ["DOOSERVICE_BUILD_PROVIDER"]
        if self.provider not in BUILD_PROVIDERS:
            raise BuildError(f"unknown provider {self.provider}")
        self.model = environ["DOOSERVICE_BUILD_MODEL"]
        self.key = environ["DOOSERVICE_BUILD_KEY"]
        self.base_url = environ.get("DOOSERVICE_BUILD_BASE_URL", "").rstrip("/")
        self.max_output_tokens = int(environ.get("DOOSERVICE_BUILD_MAX_OUTPUT_TOKENS") or 0)
        self.module = environ["DOOSERVICE_BUILD_MODULE"]
        if not set(self.module) <= BUILD_MODULE_CHARACTERS or self.module.startswith("x_"):
            raise BuildError(f"{self.module} is not a module name")
        self.directory = os.path.realpath(environ["DOOSERVICE_BUILD_DIR"])
        if not self.directory.startswith(os.path.realpath(REPOSITORY) + os.sep):
            raise BuildError(f"{self.directory} is not inside {REPOSITORY}")
        self.prompt = environ["DOOSERVICE_BUILD_PROMPT"]
        self.version = environ.get("ODOO_VERSION", "")
        self.environ = {name: value for name, value in environ.items() if not name.startswith(BUILD_KEPT_OUT)}

    def rules(self):
        """Said to the tool on top of AGENTS.md: what this session is, and where it stops."""
        return (
            f"Odoo version is {self.version}. This is an unattended build of one request on the dooservice platform. "
            f"Create the module {self.module} in {self.directory} and touch nothing outside it. Its database is a "
            "scratch one with the project's modules and no records: install and test against it with odoo-bin and "
            "dooservice, never against another database. No new field starts with x_; the only x_ names allowed "
            "are those the request says to adopt, declared exactly as they are made by hand. The module never "
            "changes or deletes existing records: adopting links them to xml ids and leaves their values alone. "
            "A marker starting with DOOSERVICE_ADOPTED_CODE_ stands for code made by hand: put it alone, exactly "
            "as it is, as the text of its field in the XML, and never rewrite, split or move it. "
            "Automations and scheduled actions it adds send nothing and run nothing while it installs. Do not "
            "commit, push or change git remotes: the platform does. End with a short summary of what the module "
            "adds, for the person who asked, in the language the request asks for."
        )

    def child_environment(self, key_name):
        environment = dict(self.environ, DOOSERVICE_AI_SESSION="1", DISABLE_AUTOUPDATER="1", HOME=os.path.expanduser("~"))
        environment[key_name] = self.key
        return environment

    @staticmethod
    def instructions():
        return f"{AI_DIR}/AGENTS.md"
