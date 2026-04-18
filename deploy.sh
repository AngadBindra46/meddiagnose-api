#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# Deploy meddiagnose-api to Google Cloud Run
# ─────────────────────────────────────────────
#
# Prerequisites:
#   1. gcloud CLI installed and authenticated
#   2. Artifact Registry repo created:
#      gcloud artifacts repositories create meddiagnose \
#        --repository-format=docker --location=us-central1
#   3. Secrets stored in Secret Manager:
#      gcloud secrets create meddiagnose-database-url --data-file=-
#      gcloud secrets create meddiagnose-redis-url --data-file=-
#      gcloud secrets create meddiagnose-secret-key --data-file=-
#
# Usage:
#   ./deploy.sh                        # Deploy with defaults
#   ./deploy.sh --region=asia-south1   # Deploy to Mumbai

REGION="${REGION:-us-central1}"
PROJECT_ID=$(gcloud config get-value project)
REPO="meddiagnose"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/meddiagnose-api"
TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")

echo "Deploying meddiagnose-api"
echo "  Project:  ${PROJECT_ID}"
echo "  Region:   ${REGION}"
echo "  Image:    ${IMAGE}:${TAG}"
echo ""

# Build and push
echo "Building container image..."
docker build -t "${IMAGE}:${TAG}" -t "${IMAGE}:latest" -f Dockerfile.prod .

echo "Pushing to Artifact Registry..."
docker push "${IMAGE}:${TAG}"
docker push "${IMAGE}:latest"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy meddiagnose-api \
  --image "${IMAGE}:${TAG}" \
  --region "${REGION}" \
  --platform managed \
  --port 8000 \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 80 \
  --set-env-vars "DEBUG=false,LOG_FORMAT=json,USE_REDIS_FOR_LIMITER=true,STORAGE_BACKEND=gcs" \
  --set-secrets "DATABASE_URL=meddiagnose-database-url:latest,REDIS_URL=meddiagnose-redis-url:latest,SECRET_KEY=meddiagnose-secret-key:latest" \
  --allow-unauthenticated

URL=$(gcloud run services describe meddiagnose-api --region "${REGION}" --format 'value(status.url)')
echo ""
echo "Deployed successfully!"
echo "  URL: ${URL}"
echo "  Health: ${URL}/health"
