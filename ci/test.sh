#!/bin/bash

function finish {
  docker-compose -f ci/compose-for-test.yml logs
  docker-compose -f ci/compose-for-test.yml down
}

set -eu

trap finish EXIT

# env
echo "Test script started"
echo "-> Project: ${CIRCLE_PROJECT_REPONAME}"
echo "-> Branch: ${CIRCLE_BRANCH}"
echo "-> Workflow: ${CIRCLE_WORKFLOW_ID}"
echo "-> Build nr. ${CIRCLE_BUILD_NUM}"

# spawn test env
IMAGE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:wf-${CIRCLE_WORKFLOW_ID}"
echo "Use docker image ${IMAGE}"

docker-compose -p ci -f ci/compose-for-test.yml up -d
sleep 5

docker run \
  -e APP_DB_NAME=testdb \
  --network ci_backend \
  $IMAGE ./manage.py test
