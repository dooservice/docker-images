# Contributing

Thank you for helping. This repository builds the images that Dooservice servers run in
production, so changes are reviewed with that in mind.

## Before you start

- **Bugs**: open an issue with the image, its tag and how to reproduce it.
- **Changes**: for anything beyond a small fix, open an issue first and describe what you
  want to change and why. It saves you work if the idea does not fit.
- **Questions**: write to [support@dooservice.sh](mailto:support@dooservice.sh).
- **Vulnerabilities**: never in an issue. See [SECURITY.md](SECURITY.md).

## Making a change

1. Fork the repository and clone it with its submodule:
   `git clone --recurse-submodules`.
2. Run `make check` before every push: it is what CI runs on every pull request.
3. Build the image you changed, `make build IMAGE=<odoo|operator|postgres|status>
   VERSION=<odoo version>`, and check that it starts: an Odoo image must serve its login
   page, a console must open a shell, the status page must answer on port 8080. Nothing
   local is ever pushed.
4. Keep each pull request to one change, and fill in its template.

The Odoo skills live in [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills):
change them there, not in `operator/skills`. The console's own skill, `dooservice-console`,
lives here, in `operator/rootfs/opt/dooservice/ai/skills/dooservice/`.

## Linting and testing

`make check` runs both; each part also runs on its own:

| Command | What it checks |
|---|---|
| `make hadolint` | Every Dockerfile, with `.hadolint.yaml` |
| `make shellcheck` | Every shell script, with `.shellcheckrc` |
| `make ruff` | `ruff check` and `ruff format --check` on all Python but `odoo/cli-patches`, with `ruff.toml` |
| `make actionlint` | The GitHub workflows |
| `make bake` | `docker-bake.hcl` is valid |
| `make skills` | Every Odoo version has its skills, and every skill is named as its directory |
| `make compile` | All Python compiles |
| `make unittest` | The status page's and the console's tests |

You need Docker with Buildx, GNU Make, `jq`, [uv](https://docs.astral.sh/uv/) (the
linters run through `uvx` at pinned versions) and
[hadolint](https://github.com/hadolint/hadolint/releases) on your `PATH`. Add tests only
where a change needs them; do not run builds you do not need.

## Code rules

- **English** in code, identifiers, docstrings, comments and commit messages. Spanish only
  in the `es` lines of the changelog's Novedades.
- **Small classes**: behaviour lives in a small class with one job; no loose module-level
  functions.
- **No regular expressions**: validate with what the standard library offers or short,
  plain string rules.
- **No inline comments** between lines of code: docstrings, a header comment at the top of
  a file, and tool directives only.
- **Constants** in the package's `constants.py`, each documented with a `#:` comment above
  it; nothing duplicated.
- **Shell** scripts are bash, start with `set -euo pipefail` and quote every variable.
- **Pins**: every base image by digest, every action by commit, every tool at an exact
  version. Renovate proposes updates weekly.
- The Python in `odoo/cli-patches` is copied from Odoo and follows Odoo's code, not these
  rules.

## Commits

One logical change per commit, small enough to review on its own, with a one-line
subject in the [Conventional Commits](https://www.conventionalcommits.org) style that says
what the change does for whoever uses it:

    fix(operator): the console opens when the repository has no requirements.txt
    build(odoo): pin the official image by digest
    ci: lint every pull request
    docs: how to build an image locally

Every commit carries a `Signed-off-by` line, which says you wrote the change or have the
right to submit it under this project's license, as the
[Developer Certificate of Origin](https://developercertificate.org) describes. Add it with
`git commit -s`.

## Changelog

Every build gets an entry in [CHANGELOG.md](CHANGELOG.md) under its revision. When
customers notice the change, the entry starts with `### Novedades`: one line per change
and language, `- es:` and `- en:`, written for people who use Odoo. The agent reads that
heading by name and does not sign a platform with a build that has none, so keep the
heading and the format exactly. Technical sections (`### Added`, `### Changed`,
`### Fixed`, `### Removed`, `### Security`) follow, in English.

## Code of conduct

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md). Report unacceptable
behaviour to [support@dooservice.sh](mailto:support@dooservice.sh).

## License

By contributing, you agree that your contribution is licensed under the
[AGPL-3.0](LICENSE), like the rest of the repository.
