#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
# Each build also gets a tag that never moves, its revision, so the digest a platform
# pinned stays tagged in the registry for as long as any server may still pull it.
# The revision the build workflow decided for every image it builds, or today by hand.
STAMP="${REVISION:-$(date -u +%Y%m%d)}"
# No version of its own: `latest` moves with each build, and the revision is the date alone.

echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-status:latest..."
docker buildx build \
    --platform linux/amd64 \
    -t "${REGISTRY}/${DOCKER_ORG}/dooservice-status:latest" \
    -t "${REGISTRY}/${DOCKER_ORG}/dooservice-status:${STAMP}" \
    --push \
    -f Dockerfile .

echo "Status image pushed to ${REGISTRY}/${DOCKER_ORG}."
