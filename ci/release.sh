#!/bin/bash

set -eu

# TODO Do this only if it's not a pull request
# TODO      and / or assumption on the branch used

REF=$1

# env
echo "Release script started"
echo "-> Project: ${CIRCLE_PROJECT_REPONAME}"
echo "-> Ref: ${REF}"
echo "-> Tag: ${CIRCLE_TAG}"
echo "-> Workflow: ${CIRCLE_WORKFLOW_ID}"
echo "-> Build nr. ${CIRCLE_BUILD_NUM}"

# check version consistency
# TODO
#PACKAGE_VERSION=$(jq -r .version package.json)
#if [ "v$PACKAGE_VERSION" != "$CIRCLE_TAG" ]; then
#  >&2 echo "Error: Version in package json (v${PACKAGE_VERSION}) does not match git tag (${CIRCLE_TAG})"
#  exit 1
#fi

# build the project
IMAGE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:${REF}"
RELEASE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:${CIRCLE_TAG}"
LATEST="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:latest"

docker pull $IMAGE
docker tag $IMAGE $RELEASE
docker tag $IMAGE $LATEST
docker push $RELEASE
docker push $LATEST
