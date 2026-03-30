#!/bin/bash
set -e

DOCKER_ORG="dooservice"
VERSIONS=("16.0" "17.0" "18.0" "19.0")

for VERSION in "${VERSIONS[@]}"; do
    echo "=== Building dooservice-odoo:${VERSION} ==="
    docker buildx build \
        --platform "linux/amd64" \
        --build-arg "ODOO_VERSION=${VERSION}" \
        -t "${DOCKER_ORG}/dooservice-odoo:${VERSION}" \
        --push \
        -f Dockerfile .

    echo "=== Done: ${VERSION} ==="
done

echo "All images built and pushed successfully."
