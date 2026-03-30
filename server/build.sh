#!/bin/bash
set -e

DOCKER_ORG="dooservice"
IMAGE_NAME="dooservice-server"
SERVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../server" && pwd)"
TAG="${1:-latest}"

echo "=== Building ${DOCKER_ORG}/${IMAGE_NAME}:${TAG} ==="

docker buildx build \
    --platform "linux/amd64" \
    -t "${DOCKER_ORG}/${IMAGE_NAME}:${TAG}" \
    --push \
    -f "${SERVER_DIR}/Dockerfile" \
    "${SERVER_DIR}"

echo "=== Done: ${DOCKER_ORG}/${IMAGE_NAME}:${TAG} ==="
