#!/bin/bash

set -eu

# TODO Do this only if it's not a pull request
# TODO      and / or assumption on the branch used

SWARM=$1
REF=$2

# Config. This should match infra deployment stack
PROJECT="arcv2"
MICROSERVICE="platform"

# env
echo "Depoy script started"
echo "-> Project: ${CIRCLE_PROJECT_REPONAME}"
echo "-> Swarm: ${SWARM}"
echo "-> Ref: ${REF}"
echo "-> Workflow: ${CIRCLE_WORKFLOW_ID}"
echo "-> Build nr. ${CIRCLE_BUILD_NUM}"
echo "-> Environment: ${ENVIRONMENT}"

# config
SWARM_MASTER=${SWARM}
SWARM_USER=ubuntu
IMAGE="apptitudestudio/${CIRCLE_PROJECT_REPONAME}:${REF}"
SERVICE_NAME="${PROJECT}-${ENVIRONMENT}_${MICROSERVICE}"

echo "Deploy image ${IMAGE} on ${SERVICE_NAME}"
ssh -o StrictHostKeyChecking=no ${SWARM_USER}@${SWARM_MASTER} "sudo docker service update --with-registry-auth --image $IMAGE $SERVICE_NAME"
