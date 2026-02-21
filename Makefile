IMAGE ?= expert-finder-api:local
ENV_FILE ?= .env
LOG_LEVEL ?= DEBUG
PLATFORM ?= linux/amd64
BUILDER ?= ef-builder

.PHONY: docker-build docker-run-api docker-run-caddy docker-shell load-env gcp-init gcp-create-repo docker-push-registry gcp-deploy gcp-sync-secrets gcp-grant-secret-access gcp-release

docker-build:
	docker build -t $(IMAGE) .

docker-run-api:
	docker run --rm -p 8000:8000 --env-file $(ENV_FILE) -e LOG_LEVEL=$(LOG_LEVEL) $(IMAGE)

docker-run-caddy:
	docker run --rm --name expert-caddy -p 80:80 -p 443:443 -v "$$PWD/Caddyfile:/etc/caddy/Caddyfile" caddy:2

docker-shell:
	docker run -it --rm $(IMAGE) /bin/sh

load-env:
	@. scripts/shell_scripts/load_env.sh && echo "IMAGE_URI=$$IMAGE_URI"

docker-push-registry:
	@. scripts/shell_scripts/load_env.sh && \
	: "$$IMAGE_URI" && \
	docker buildx create --use --name $(BUILDER) >/dev/null 2>&1 || true && \
	docker buildx build \
		--platform $(PLATFORM) \
		-t "$$IMAGE_URI" \
		--push \
		.

gcp-init:
	@. scripts/shell_scripts/load_env.sh && \
	: "$$PROJECT_ID" && \
	gcloud auth login && \
	gcloud config set project "$$PROJECT_ID" && \
	gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcp-create-repo:
	@. scripts/shell_scripts/load_env.sh && \
	: "$$REPO" "$$REGION" && \
	gcloud artifacts repositories create "$$REPO" \
		--repository-format=docker \
		--location="$$REGION" \
		--description="Expert Finder images" || true

gcp-sync-secrets:
	@bash scripts/shell_scripts/sync_secrets.sh

gcp-grant-secret-access:
	@bash scripts/shell_scripts/grant_secret_access.sh

gcp-deploy:
	@. scripts/shell_scripts/load_env.sh && \
	: "$$SERVICE" "$$IMAGE_URI" "$$REGION" "$$API_ENVIRONMENT" "$$COOKIE_SECURE" "$$EXPERT_FINDER_BACKEND" "$$ACCESS_TOKEN_EXPIRE_MINUTES" && \
	gcloud run deploy "$$SERVICE" \
		--image "$$IMAGE_URI" \
		--region "$$REGION" \
		--platform managed \
		--allow-unauthenticated \
		--port 8000 \
		--set-env-vars "API_ENVIRONMENT=$$API_ENVIRONMENT,COOKIE_SECURE=$$COOKIE_SECURE,EXPERT_FINDER_BACKEND=$$EXPERT_FINDER_BACKEND,ACCESS_TOKEN_EXPIRE_MINUTES=$$ACCESS_TOKEN_EXPIRE_MINUTES" \
		--set-secrets "INFISICAL_PROJECT_ID=INFISICAL_PROJECT_ID:latest,INFISICAL_USER=INFISICAL_USER:latest,INFISICAL_KEY=INFISICAL_KEY:latest,APP_TEST_PASSWORD=APP_TEST_PASSWORD:latest,OAUTH2_SECRET_KEY=OAUTH2_SECRET_KEY:latest,DATABASE_URL=DATABASE_URL:latest"

gcp-release: docker-build docker-push-registry gcp-deploy
