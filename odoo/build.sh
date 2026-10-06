#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
VERSIONS=("16.0" "17.0" "18.0" "19.0" "20.0")
ONLY="${1:-}"

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
        --push \
        -f Dockerfile .
done

echo "Odoo images pushed to ${REGISTRY}/${DOCKER_ORG}."
