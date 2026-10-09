#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
VERSIONS=("16.0" "17.0" "18.0" "19.0" "20.0")
ONLY="${1:-}"
# Each build also gets a tag that never moves, its revision, so the digest a platform
# pinned stays tagged in the registry for as long as any server may still pull it.
# The revision the build workflow decided for every image it builds, or today by hand:
# 20261010, and 20261010-2 when that day already has one.
STAMP="${REVISION:-$(date -u +%Y%m%d)}"

for VERSION in "${VERSIONS[@]}"; do
    if [ -n "${ONLY}" ] && [ "${ONLY}" != "${VERSION}" ]; then
        continue
    fi

    BASE="odoo:${VERSION}"
    echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION} on ${BASE}..."
    docker buildx build \
        --platform linux/amd64 \
        --build-arg "ODOO_VERSION=${VERSION}" \
        --build-arg "ODOO_BASE=${BASE}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION}-${STAMP}" \
        --push \
        -f Dockerfile .
done

echo "Odoo images pushed to ${REGISTRY}/${DOCKER_ORG}."
