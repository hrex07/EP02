# Deployment Guide: EP02 Pentominoes

This document describes how to deploy the Pentominoes game to Google Cloud Run.

## Prerequisites

1.  **Google Cloud Project**: Create a project and enable the following APIs:
    *   Cloud Run API
    *   Artifact Registry API
    *   Cloud Build API
2.  **Service Account**: Create a Service Account with `Cloud Run Admin` and `Storage Admin` roles.
3.  **Artifact Registry**: Create a Docker repository named `pentominoes-repo` in `us-central1`.

## GitHub Secrets

Add the following secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret | Description |
| :--- | :--- |
| `GCP_PROJECT` | Your Google Cloud Project ID. |
| `GCP_SA_KEY` | The JSON key of your Service Account. |

## CI/CD Pipeline

The `.github/workflows/deploy.yml` workflow automatically deploys to Cloud Run on every push to the `main` branch.

### Workflow Steps:
1.  **Builds** the Docker image for the backend.
2.  **Pushes** the image to Google Artifact Registry.
3.  **Deploys** the container to Google Cloud Run.

## Environment Variables

The backend service supports the following environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | Comma-separated list of allowed CORS origins. |
| `PORT` | `8000` | Port for the FastAPI server (Cloud Run provides this). |

## Troubleshooting

### 1. "Permission Denied" during deployment
Ensure the Service Account has `Service Account User` role on the project to allow it to act as the Cloud Run service identity.

### 2. "CORS Error" in browser
Check the `ALLOWED_ORIGINS` environment variable in the Cloud Run service configuration. It must include the exact URL of your frontend (e.g., `https://your-frontend-service.a.run.app`).

### 3. "Image not found" in Cloud Run
Verify that the image path in `deploy.yml` matches your Artifact Registry path.

### 4. Build fails in GitHub Actions
Check the Docker build logs. Ensure `backend/requirements.txt` and `frontend/package.json` are up to date.
