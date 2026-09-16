# docker-images

Custom Docker images for the dooservice infrastructure stack.

## Images

| Image | Versions | Description |
|---|---|---|
| `ghcr.io/dooservice/dooservice-odoo` | `16.0` `17.0` `18.0` `19.0` | Odoo with unified CLI patches and dooservice user (uid 1500) |
| `ghcr.io/dooservice/dooservice-operator` | `16.0` `17.0` `18.0` `19.0` | Console for an environment: shell, psql, git, Claude Code, opencode and the `dooservice` command |
| `ghcr.io/dooservice/dooservice-postgres` | `16` `17` `18` | PostgreSQL with pgvector, unaccent and md5 auth for PgDog |

## Build & push

Requires Docker Buildx and an authenticated ghcr.io session:

```bash
docker login ghcr.io
```

```bash
# Build and push all Odoo versions (16, 17, 18, 19)
cd odoo && ./build.sh

# Build and push all operator versions (after the Odoo images)
cd operator && ./build.sh

# Build and push all Postgres versions (16, 17, 18)
cd postgres && ./build.sh

```

## odoo

Based on the official `odoo` image. Adds:

- **dooservice user** (uid/gid 1500) — matches the host agent user, avoids volume permission issues
- **CLI patches** — unifies `odoo db dump` / `odoo db load` across v16–v19 so the agent can use a single command format
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
