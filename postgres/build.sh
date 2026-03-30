#!/bin/bash
set -e

DOCKER_ORG="dooservice"
VERSIONS=("16" "17" "18")

for VERSION in "${VERSIONS[@]}"; do
    echo "=== Building dooservice-postgres:${VERSION} ==="
    docker buildx build \
        --platform "linux/amd64" \
        --build-arg "PG_VERSION=${VERSION}" \
        -t "${DOCKER_ORG}/dooservice-postgres:${VERSION}" \
        --push \
        -f Dockerfile .

    echo "=== Done: ${VERSION} ==="
done

echo "All PostgreSQL images built and pushed successfully."
