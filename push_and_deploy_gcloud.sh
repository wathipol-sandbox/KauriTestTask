#!/bin/bash

# Access variables using their names from the environment
BRANCH=$(git rev-parse --abbrev-ref HEAD)
ENVIRONMENT=${ENVIRONMENT:-"PROD"}  # Set default if not defined in .env
RESTAPI_DOCKERFILE=${RESTAPI_DOCKERFILE:-"Dockerfile.prod"}
CLOUD_STORAGE=${CLOUD_STORAGE:-"europe-central2-docker.pkg.dev/<project_id>/<gar_storage>}"}

SHA=$(git rev-parse HEAD)
echo "commit sha ${SHA}"


if [[ "$ENVIRONMENT" = "PROD" ]]; then
  echo "Building PROD environment";
  RESTAPI_CLOUD_RUN_TAG="${CLOUD_STORAGE}/rest_api_prod:${BRANCH}-${SHA}"
else
  echo "Script only for PROD environment..."
  exit 1;
fi

# build dockers
echo "building from ${PWD}/${RESTAPI_DOCKERFILE}"
docker build --build-arg ENVIRONMENT=${ENVIRONMENT} -f ${PWD}/${RESTAPI_DOCKERFILE} ${PWD} -t ${RESTAPI_CLOUD_RUN_TAG}

# push dockers
docker push "${RESTAPI_CLOUD_RUN_TAG}"
RESTAPI_SHA=$(docker inspect --format='{{index .RepoDigests 0}}' ${RESTAPI_CLOUD_RUN_TAG}  | perl -wnE'say /sha256.*/g')
echo "$RESTAPI_SHA"


# Deploy cloud runs
echo "Deploying rest-api"
gcloud run deploy rest-api-prod \
--image=${CLOUD_STORAGE}/rest_api_prod@${RESTAPI_SHA} \
--region=europe-central2 \
--project=${GCP_PROJECT_ID}
&& gcloud run services update-traffic rest-api-prod --to-latest \
--region=europe-central2 \
--project=${GCP_PROJECT_ID} 

echo "Done deploying cloud run"
