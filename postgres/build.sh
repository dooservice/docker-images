#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
# Each build also gets a tag that never moves, so the digest a platform pinned stays
# tagged in the registry for as long as any server may still pull it.
STAMP="$(date -u +%Y%m%d%H%M)"
VERSIONS=("16" "17" "18")

for VERSION in "${VERSIONS[@]}"; do
    echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-postgres:${VERSION}..."
    docker buildx build \
        --platform linux/amd64 \
        --build-arg "PG_VERSION=${VERSION}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-postgres:${VERSION}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-postgres:${VERSION}-${STAMP}" \
        --push \
        -f Dockerfile .
done

echo "All Postgres images pushed to ${REGISTRY}/${DOCKER_ORG}."
