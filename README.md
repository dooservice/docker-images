# docker-images

Custom Docker images for the dooservice infrastructure stack.

## Images

| Image | Versions | Description |
|---|---|---|
| `ghcr.io/dooservice/dooservice-odoo` | `16.0` `17.0` `18.0` `19.0` `20.0` | Odoo with unified CLI patches and dooservice user (uid 1500) |
| `ghcr.io/dooservice/dooservice-operator` | `16.0` `17.0` `18.0` `19.0` `20.0` | Console for an environment: shell, psql, git, Claude Code, opencode and the `dooservice` command |
| `ghcr.io/dooservice/dooservice-postgres` | `16` `17` `18` | PostgreSQL with pgvector, unaccent and md5 auth for PgDog |
| `ghcr.io/dooservice/dooservice-case-runner` | `1` | Talks to the model during a case; no shell, no Odoo, nothing to reach the database with |

## Build & push

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

# Build and push the case runner
cd case-runner && ./build.sh

```

### What servers run

Servers never run these tags as they are. A platform (`make platform` in the agent
repository) resolves each tag listed in its `platform.toml` to the digest it has at that
moment and signs it; servers pull that digest, whatever the tag points at later. A new
image reaches servers only through a new platform, ring by ring. Every build also pushes
`<version>-<yyyymmddhhmm>`, which never moves, so a pinned digest stays tagged.

## odoo

Based on the official `odoo` image for every version, 20.0 included since Odoo published
it. Adds:

- **dooservice user** (uid/gid 1500) — matches the host agent user, avoids volume permission issues
- **CLI patches** — unifies `odoo db dump` / `odoo db load` across v16–v20 so the agent can use a single command format (v19 and v20 already ship them)
- **entrypoint** — auto-installs pip dependencies from any `requirements.txt` found in `/mnt/extra-addons` before starting Odoo

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
  ask the platform to hold deploys, and open the agent in the environment's repository with
  the managed settings and `AGENTS.md` from `/opt/dooservice/ai`
- **`dooservice`** — install, update, test and shell run here; restart, logs and status are
  asked of the agent over the session's control socket, since this container cannot touch
  any other. There is no push: the container holds no git credentials
- **`odoo-bin`** wrapper that injects the database connection, so it is never passed by hand
- **Welcome banner and prompt** in `/etc/profile.d/dooservice.sh`

## case-runner

The container a case turn runs in. It holds the conversation with the model and nothing
else: no shell, no Odoo, no database client, running as uid 1600 with a read-only root
filesystem. Everything it wants to know about the customer's Odoo it has to ask the agent
for, over the pipe it was started with, and the agent answers through the bridge — which
is what keeps a model from reaching a database directly even if it asks nicely.

It also runs in draft mode, where it is given the operations of a pass and writes the
script that would prove them. What comes back is JSON or it is refused; prose is not an
answer the platform can run.

```bash
cd case-runner && ./build.sh        # builds and pushes ghcr.io/dooservice/dooservice-case-runner:1
uv run pytest                       # its own tests, no network and no model
```
