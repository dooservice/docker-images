#!/bin/bash
set -e

REGISTRY="ghcr.io"
DOCKER_ORG="dooservice"
# The versions are the ones the agent's platform.toml offers, beside this repository by hand
# and fetched by the build workflow.
PLATFORM_TOML="${PLATFORM_TOML:-../../dooservice-agent/platform.toml}"
[ -f "${PLATFORM_TOML}" ] || { echo "No platform.toml at ${PLATFORM_TOML}; set PLATFORM_TOML." >&2; exit 1; }
mapfile -t VERSIONS < <(python3 ../versions.py "${PLATFORM_TOML}")
ONLY="${1:-}"
# Each build also gets a tag that never moves, its revision, so the digest a platform
# pinned stays tagged in the registry for as long as any server may still pull it.
# The revision the build workflow decided for every image it builds, or today by hand:
# 20261010, and 20261010-2 when that day already has one.
STAMP="${REVISION:-$(date -u +%Y%m%d)}"

case " ${VERSIONS[*]} " in
    *" ${ONLY:-${VERSIONS[0]}} "*) ;;
    *) echo "Odoo ${ONLY} is not in [odoo] of ${PLATFORM_TOML}." >&2; exit 1 ;;
esac

for VERSION in "${VERSIONS[@]}"; do
    if [ -n "${ONLY}" ] && [ "${ONLY}" != "${VERSION}" ]; then
        continue
    fi

    BASE="odoo:${VERSION}"
    ADDONS_COMMIT="$(python3 ../addons.py addons.toml "${VERSION}")"
    echo "Building ${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION} on ${BASE}..."
    docker buildx build \
        --platform linux/amd64 \
        --build-arg "ODOO_VERSION=${VERSION}" \
        --build-arg "ODOO_BASE=${BASE}" \
        --build-arg "ADDONS_COMMIT=${ADDONS_COMMIT}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION}" \
        -t "${REGISTRY}/${DOCKER_ORG}/dooservice-odoo:${VERSION}-${STAMP}" \
        --push \
        -f Dockerfile .
done

echo "Odoo images pushed to ${REGISTRY}/${DOCKER_ORG}."
