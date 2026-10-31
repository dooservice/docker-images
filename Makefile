# Lint, test and build the images on your own machine. Nothing here pushes: `make build`
# loads one image into the local Docker, and only the Build workflow pushes to ghcr.io.
#
#   make check                          lint and test, what CI runs on every pull request
#   make build IMAGE=odoo VERSION=19.0  one image, loaded locally
#   make print                          the bake definition every image is built from
#
# The linters run through uvx (https://docs.astral.sh/uv/), except hadolint, which must be
# on the PATH (https://github.com/hadolint/hadolint/releases).

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := check

IMAGE ?= odoo
VERSION ?= 19.0

PYTHON ?= python3
HADOLINT ?= hadolint
RUFF ?= uvx ruff@0.17.3
SHELLCHECK ?= uvx --from shellcheck-py==0.11.0.1 shellcheck
ACTIONLINT ?= uvx --from actionlint-py==1.7.12.25 actionlint

PYTHON_SCRIPTS := $(filter-out %/__pycache__,$(wildcard operator/rootfs/usr/local/bin/* operator/rootfs/opt/dooservice/git-hooks/dispatch))
SKILLS := operator/skills/odoo/*/*/SKILL.md operator/rootfs/opt/dooservice/ai/skills/dooservice/*/SKILL.md

ifneq ($(filter $(IMAGE),odoo operator),)
TARGET := $(IMAGE)-$(subst .,-,$(VERSION))
else
TARGET := $(IMAGE)
endif

.PHONY: check lint test hadolint shellcheck ruff actionlint bake skills compile unittest build print

check: lint test

lint: hadolint shellcheck ruff actionlint bake skills

test: compile unittest

hadolint:
	$(HADOLINT) $$(git ls-files -- '*Dockerfile')

shellcheck:
	$(SHELLCHECK) $$(git ls-files -- '*.sh')

ruff:
	$(RUFF) check .
	$(RUFF) format --check .

actionlint:
	$(ACTIONLINT)

bake:
	docker buildx bake --print > /dev/null

skills:
	for version in $$(docker buildx bake --print odoo | jq -r '.target[].args.ODOO_VERSION'); do \
	  test -d "operator/skills/odoo/$${version}" \
	    || { echo "Odoo $${version} has no skills in operator/skills/odoo/$${version}" >&2; exit 1; }; \
	done
	for skill in $(SKILLS); do \
	  name="$$(basename "$$(dirname "$${skill}")")"; \
	  grep -qx "name: $${name}" "$${skill}" \
	    || { echo "$${skill} is not named $${name}" >&2; exit 1; }; \
	done

compile:
	export PYTHONPYCACHEPREFIX="$$(mktemp -d)"; \
	$(PYTHON) -m compileall -q odoo status operator/rootfs versions.py; \
	for script in $(PYTHON_SCRIPTS); do $(PYTHON) -m py_compile "$${script}"; done

unittest:
	PYTHONPATH=status $(PYTHON) -m unittest discover status/tests
	if [ -d operator/tests ]; then \
	  PYTHONPATH=operator/rootfs/opt/dooservice/lib $(PYTHON) -m unittest discover operator/tests; \
	fi

build:
	case "$(IMAGE)" in odoo|operator|postgres|status) ;; \
	  *) echo "IMAGE must be odoo, operator, postgres or status" >&2; exit 1 ;; esac
	ODOO_VERSIONS="$(VERSION)" docker buildx bake --load $(TARGET)

print:
	docker buildx bake --print
