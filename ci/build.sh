#!/bin/bash

set -eu

# env
echo "Build script started"
echo "-> Project: ${CIRCLE_PROJECT_REPONAME}"
echo "-> Branch: ${CIRCLE_BRANCH}"
echo "-> Workflow: ${CIRCLE_WORKFLOW_ID}"
echo "-> Build nr. ${CIRCLE_BUILD_NUM}"

# build the project
IMAGE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:wf-${CIRCLE_WORKFLOW_ID}"
echo "Build Docker image ${IMAGE}..."

set +u

echo "${CIRCLE_SHA1}" > build-info/SHA1
echo "${CIRCLE_TAG}" > build-info/TAG
echo "${CIRCLE_BUILD_NUM}" > build-info/BUILD

docker build -t $IMAGE .
