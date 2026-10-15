#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
# Each build also gets a tag that never moves, its revision, so the digest a platform
# pinned stays tagged in the registry for as long as any server may still pull it.
# The revision the build workflow decided for every image it builds, or today by hand.
STAMP="${REVISION:-$(date -u +%Y%m%d)}"
MAJOR="1"

echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-status:${MAJOR}..."
docker buildx build \
    --platform linux/amd64 \
    -t "${REGISTRY}/${DOCKER_ORG}/dooservice-status:${MAJOR}" \
    -t "${REGISTRY}/${DOCKER_ORG}/dooservice-status:${MAJOR}-${STAMP}" \
    --push \
    -f Dockerfile .

echo "Status image pushed to ${REGISTRY}/${DOCKER_ORG}."
