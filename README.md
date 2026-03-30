# DooService Docker Images

Docker image build scripts for all DooService infrastructure components.

## Images

| Directory | Image | Description |
|-----------|-------|-------------|
| `odoo/` | `dooservice/dooservice-odoo:{version}` | Custom Odoo image with CLI patches (v16-v19) |
| `server/` | `dooservice/dooservice-server:latest` | Server API + WebSocket + Orchestrator |
| `postgres/` | `dooservice/dooservice-postgres:16` | Shared PostgreSQL for Odoo instances |
| `pgbouncer/` | `dooservice/dooservice-pgbouncer:latest` | Connection pooler for PostgreSQL |

## Build & Push

Each directory has a `build.sh` that builds and pushes to Docker Hub:

```bash
# Odoo images (v16, v17, v18, v19)
cd odoo && ./build.sh

# Server image
cd server && ./build.sh

# Server image with specific tag
cd server && ./build.sh 0.4.0

# PostgreSQL image
cd postgres && ./build.sh

# PgBouncer image
cd pgbouncer && ./build.sh
```

## Notes

- `server/build.sh` references `../../server/Dockerfile` (the Dockerfile lives in the server repo)
- `odoo/build.sh` applies CLI patches per version via `cli-patches/apply.sh`
- All images are pushed to the `dooservice` Docker Hub organization
