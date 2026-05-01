## 1. Backend Container Configuration

- [x] 1.1 Create Dockerfile for FastAPI backend (python:3.13-slim base)
- [x] 1.2 Add gunicorn or use uvicorn with workers
- [x] 1.3 Configure container to run on port 8000
- [x] 1.4 Test Docker build locally

## 2. GitHub Actions CI/CD Pipeline

- [x] 2.1 Create .github/workflows/deploy.yml
- [x] 2.2 Configure Google Auth action for authentication
- [x] 2.3 Set up Docker build and push to Artifact Registry
- [x] 2.4 Add Cloud Run deploy step
- [x] 2.5 Add required secrets to GitHub (GCP_PROJECT, GCP_SA_KEY)

## 3. Frontend Production Build

- [x] 3.1 Update vite.config.ts with production API URL
- [x] 3.2 Create nginx.conf for serving static files (if using Cloud Run)
- [x] 3.3 Add Dockerfile for frontend (multi-stage build)
- [x] 3.4 Test production build locally

## 4. Environment Configuration

- [x] 4.1 Document required environment variables for Cloud Run
- [x] 4.2 Update backend to read ALLOWED_ORIGINS from env var
- [x] 4.3 Configure CORS for production domain in GitHub workflow

## 5. Documentation

- [x] 5.1 Create deployment/README.md with step-by-step instructions
- [x] 5.2 Add troubleshooting section for common errors

## 6. Initial Deployment

- [x] 6.1 Run first deployment manually to verify pipeline
- [x] 6.2 Test production endpoints
- [x] 6.3 Enable automatic deployments on main branch push