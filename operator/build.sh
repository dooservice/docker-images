#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
VERSIONS=("16.0" "17.0" "18.0" "19.0")

for VERSION in "${VERSIONS[@]}"; do
    echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-operator:${VERSION}..."
    docker buildx build \
        --platform linux/amd64 \
        --build-arg "ODOO_VERSION=${VERSION}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-operator:${VERSION}" \
        --push \
        -f Dockerfile .
done

echo "All operator images pushed to ${REGISTRY}/${DOCKER_ORG}."
