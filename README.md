# docker-images

Custom Docker images for the dooservice infrastructure stack.

## Images

| Image | Versions | Description |
|---|---|---|
| `ghcr.io/dooservice/dooservice-odoo` | `16.0` `17.0` `18.0` `19.0` `20.0` | Odoo with unified CLI patches and dooservice user (uid 1500) |
| `ghcr.io/dooservice/dooservice-operator` | `16.0` `17.0` `18.0` `19.0` `20.0` | Console for an environment: shell, psql, git, Claude Code, opencode and the `dooservice` command |
| `ghcr.io/dooservice/dooservice-postgres` | `16` `17` `18` | PostgreSQL with pgvector, unaccent and md5 auth for PgDog |

## Build & push

Images are built on GitHub's machines, not on a server of ours — an Odoo image and its
console take some 8 GB, and a server's disk holds its customers' data:

```bash
gh workflow run build.yml --repo dooservice/docker-images                  # all of them
gh workflow run build.yml --repo dooservice/docker-images -f versions=18.0 # one version
```

Each Odoo version builds on a runner of its own, its console right after it, and Postgres
beside them. The scripts below are what the workflow runs, and still work by hand.

### By hand

Requires Docker Buildx and an authenticated ghcr.io session:

```bash
docker login ghcr.io
```

```bash
# Build and push all Odoo versions (16, 17, 18, 19, 20), or one: ./build.sh 20.0
cd odoo && ./build.sh

# Build and push all operator versions (after the Odoo images)
cd operator && ./build.sh

# Build and push all Postgres versions (16, 17, 18)
cd postgres && ./build.sh

```

### Revisions

Every build gives all its images one **revision**, its date, the way Odoo's own images are
tagged: `dooservice-odoo:18.0-20261010`, `dooservice-operator:18.0-20261010`,
`dooservice-postgres:16-20261010`. A revision never moves: a second build the same day takes
`-2`, then `-3`. Each build also moves the usual tag (`18.0`), which no server runs.

By hand, `REVISION=20261010 ./build.sh 18.0`; without it the script takes today's date.

### What is new, for customers

Each revision has an entry in [CHANGELOG.md](CHANGELOG.md) with a `### Novedades` section:
one line per change and language (`- es:`, `- en:`), written for whoever uses Odoo. It is
signed into the platform and shown in the panel to the servers that receive it, and
`make platform` refuses a build without one. Write it right after the build, before pinning.

### What servers run

Servers never run these tags as they are, and building sends nothing to any server. A
platform (`make platform` in the agent repository) resolves each tag in its `platform.toml`
to the revision and digest it has at that moment and signs it; servers pull exactly that.
The whole process: [docs/imagenes.md](https://github.com/dooservice/agent/blob/main/docs/imagenes.md)
and [docs/actualizaciones.md](https://github.com/dooservice/agent/blob/main/docs/actualizaciones.md).

## odoo

Based on the official `odoo` image for every version, 20.0 included since Odoo published
it. Adds:

- **dooservice user** (uid/gid 1500) — matches the host agent user, avoids volume permission issues
- **CLI patches** — unifies `odoo db dump` / `odoo db load` across v16–v20 so the agent can use a single command format (v19 and v20 already ship them)
- **entrypoint** — auto-installs pip dependencies from any `requirements.txt` found in `/mnt/addons` (the project's repository) before starting Odoo

## postgres

Based on the official `postgres` image. Adds:

- **pgvector** — vector similarity extension
- **unaccent** (immutable) — required for Odoo full-text search
- **md5 auth** — replaces the default `scram-sha-256` so PgDog can authenticate

## operator

Based on `dooservice-odoo` for the same version, so it has the environment's Odoo, its CLI
patches and its user (uid 1500). The agent starts one per console session, next to the
environment's container, hardened — read-only root, no capabilities, `no-new-privileges`,
a network of its own — and removes it when the session ends. Adds:

- **Claude Code, opencode and rtk** in `/opt/ai`, pinned, with auto-update off
- **Launchers** `claude` and `opencode` that refuse to run outside development environments,
  ask the platform to hold deploys, and open the AI in one of two modes, chosen in the
  panel (`DOOSERVICE_AI_MODE_CHOSEN`):
  - **code**: works in the project's repository at `/mnt/addons`, with `AGENTS.md` and
    `settings.json`; changes leave as pull requests through `dooservice publish`
  - **functional**: configures Odoo through its data and writes no code, with
    `CONFIGURATION.md` and file editing denied; the agent mounts the repository read-only.
    A console without a repository is always functional

  Claude Code loads the mode's instructions from `~/.claude/CLAUDE.md`, a one-line import of
  the file in `/opt/dooservice/ai`; nothing is written into the customer's repository
- **Skills** in `/opt/dooservice/ai/skills`, linked into each tool's skills directory by mode:
  the Odoo skills of the image's version and `dooservice-console`/`odoo-upgrade` in code
  mode, `odoo-functional` in functional mode. They live in the public
  [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills) repository, a
  submodule at `operator/skills`: clone this one with `--recurse-submodules`, and bump the
  submodule to take new skills
- **`dooservice`**: install, update, test and shell run here; restart, logs and status are
  asked of the agent over the session's control socket, since this container cannot touch
  any other. `publish` pushes what was committed and opens its pull requests; the push is
  done by the agent with the account's token, never from this container, which holds no git
  credentials
- **`psql`** wrapper: read-only in functional mode
- **Git hooks** in `/opt/dooservice/git-hooks` (`core.hooksPath` in `/etc/gitconfig`): a commit
  made by an AI session gets `Co-authored-by: Dooservice <noreply@dooservice.sh>`, once; then
  the repository's own hook of the same name runs, if it has one
- **`odoo-bin`** wrapper that injects the database connection, so it is never passed by hand,
  and refuses another `--addons-path` in functional mode
- **Welcome banner and prompt** in `/etc/profile.d/dooservice.sh`

