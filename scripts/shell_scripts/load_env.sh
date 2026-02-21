#!/usr/bin/env bash

set -a
source .env
set +a

export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:${IMAGE_TAG}"
