#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/load_env.sh"

required_vars=(
  PROJECT_ID
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required env var: ${var_name}" >&2
    exit 1
  fi
done

PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
RUNTIME_SA="${CLOUD_RUN_RUNTIME_SA:-${PROJECT_NUMBER}-compute@developer.gserviceaccount.com}"

secrets=(
  INFISICAL_PROJECT_ID
  INFISICAL_USER
  INFISICAL_KEY
  APP_TEST_PASSWORD
  OAUTH2_SECRET_KEY
  DATABASE_URL
)

for secret_name in "${secrets[@]}"; do
  gcloud secrets add-iam-policy-binding "${secret_name}" \
    --member="serviceAccount:${RUNTIME_SA}" \
    --role="roles/secretmanager.secretAccessor" >/dev/null
  echo "Granted roles/secretmanager.secretAccessor on ${secret_name} to ${RUNTIME_SA}"
done
