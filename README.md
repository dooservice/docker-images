# DooService Docker Images

Docker image build scripts for all DooService infrastructure components.

## Images

| Directory | Image | Description |
|-----------|-------|-------------|
| `odoo/` | `dooservice/dooservice-odoo:{version}` | Custom Odoo image with CLI patches (v16-v19) |
| `postgres/` | `dooservice/dooservice-postgres:16` | Shared PostgreSQL for Odoo instances |

> **Note:** The server image (`dooservice/dooservice-server`) is built from the [server repo](https://github.com/DooService/server) using `server/build.sh`.

## Build & Push

Each directory has a `build.sh` that builds and pushes to Docker Hub:

```bash
# Odoo images (v16, v17, v18, v19)
cd odoo && ./build.sh

# PostgreSQL image
cd postgres && ./build.sh
```

## Notes

- `odoo/build.sh` applies CLI patches per version via `cli-patches/apply.sh`
- All images are pushed to the `dooservice` Docker Hub organization
