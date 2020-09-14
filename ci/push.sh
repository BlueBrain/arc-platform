#!/bin/bash

set -eu

REF=$1

# TODO Do this only if it's not a pull request
# TODO      and / or assumption on the branch used

# env
echo "Push script started"
echo "-> Project: ${CIRCLE_PROJECT_REPONAME}"
echo "-> Ref: ${REF}"
echo "-> Workflow: ${CIRCLE_WORKFLOW_ID}"
echo "-> Build nr. ${CIRCLE_BUILD_NUM}"

# build the project
IMAGE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:wf-${CIRCLE_WORKFLOW_ID}"
SNAPSHOT="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:${REF}"

docker tag $IMAGE $SNAPSHOT
docker push $SNAPSHOT

