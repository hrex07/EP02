## Why

The pentominoes game needs to be deployed to production so users can access it via the web. Google Cloud Run provides a scalable, serverless container platform ideal for this FastAPI backend.

## What Changes

- Create Cloud Run deployment configuration (Dockerfile, cloudbuild.yaml)
- Set up CI/CD pipeline for automated deployments
- Configure environment variables for Cloud Run (Firestore, CORS)
- Add deployment documentation with step-by-step instructions

## Capabilities

### New Capabilities
- `cloud-run-deployment`: CI/CD pipeline and Cloud Run configuration for deploying the backend service
- `cloud-run-frontend`: Static site deployment configuration for the React frontend (Cloud Run or Cloud Storage + CDN)

### Modified Capabilities
- None (no existing requirement changes)

## Impact

- New files: `Dockerfile`, `cloudbuild.yaml`, `.github/workflows/deploy.yml`
- New directory: `deployment/` with configs and docs
- Existing APIs (`/game/*`, `/solve`) remain unchanged
- Environment: Requires GCP project with Cloud Run API enabled