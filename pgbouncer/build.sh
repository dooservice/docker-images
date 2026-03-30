#!/bin/bash
set -e

DOCKER_ORG="dooservice"

cd "$(dirname "$0")"

echo "=== Building dooservice-pgbouncer:latest ==="
docker buildx build \
    --platform "linux/amd64" \
    -t "${DOCKER_ORG}/dooservice-pgbouncer:latest" \
    --push \
    -f Dockerfile .

echo "=== Done: dooservice-pgbouncer:latest pushed successfully ==="
