#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/load_env.sh"

required_vars=(
  INFISICAL_PROJECT_ID
  INFISICAL_USER
  INFISICAL_KEY
  APP_TEST_PASSWORD
  OAUTH2_SECRET_KEY
  DATABASE_URL
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required env var: ${var_name}" >&2
    exit 1
  fi
done

upsert_secret() {
  local secret_name="$1"
  local secret_value="$2"
  printf '%s' "${secret_value}" | gcloud secrets versions add "${secret_name}" --data-file=- >/dev/null 2>&1 || \
    printf '%s' "${secret_value}" | gcloud secrets create "${secret_name}" --data-file=- --replication-policy=automatic >/dev/null
  echo "Synced secret: ${secret_name}"
}

upsert_secret "INFISICAL_PROJECT_ID" "${INFISICAL_PROJECT_ID}"
upsert_secret "INFISICAL_USER" "${INFISICAL_USER}"
upsert_secret "INFISICAL_KEY" "${INFISICAL_KEY}"
upsert_secret "APP_TEST_PASSWORD" "${APP_TEST_PASSWORD}"
upsert_secret "OAUTH2_SECRET_KEY" "${OAUTH2_SECRET_KEY}"
upsert_secret "DATABASE_URL" "${DATABASE_URL}"
