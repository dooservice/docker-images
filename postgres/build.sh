#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
# Each build also gets a tag that never moves, its revision, so the digest a platform
# pinned stays tagged in the registry for as long as any server may still pull it.
# The revision the build workflow decided for every image it builds, or today by hand:
# 20261010, and 20261010-2 when that day already has one.
STAMP="${REVISION:-$(date -u +%Y%m%d)}"
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
