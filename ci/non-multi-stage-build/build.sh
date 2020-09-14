#!/bin/bash

# This script is used to build the app in environments
# with outdated Docker not supporting multi-stage builds

set -eu

IMAGE="${1}"

mkdir -p ./build/arcv2_platform/static/assets
rm -rf ./build/arcv2_platform/static/assets/*

# env
echo "Build script started (non multi-stage)"
echo "-> Image: ${IMAGE}"

set +u

echo "Building assets..."
docker build \
    --build-arg HTTP_PROXY="$HTTP_PROXY" \
    --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$https_proxy" \
    -t arcv2-assets \
    -f ./ci/non-multi-stage-build/assets.Dockerfile \
    .

docker create --name arcv2-assets-cont arcv2-assets
docker cp arcv2-assets-cont:/build/arcv2_platform/static/assets ./build/arcv2_platform/static
docker rm -f arcv2-assets-cont

echo "Building main image..."
docker build \
    --build-arg HTTP_PROXY="$HTTP_PROXY" \
    --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$https_proxy" \
    --no-cache \
    -t $IMAGE \
    -f ./ci/non-multi-stage-build/Dockerfile \
    .
