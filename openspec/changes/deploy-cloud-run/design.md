## Context

The EP02 Pentominoes game consists of:
- **Frontend**: React 19 + TypeScript + Vite (static assets)
- **Backend**: Python FastAPI (`api.py`) running on port 8000
- **Current state**: Runs locally via `npm run dev` (frontend) and `uvicorn api:app` (backend)

Target deployment: Google Cloud Run with CI/CD via GitHub Actions.

## Goals / Non-Goals

**Goals:**
- Deploy FastAPI backend to Cloud Run with HTTPS
- Deploy React frontend (Cloud Run static or Cloud Storage + Cloud CDN)
- Set up GitHub Actions CI/CD pipeline for automatic deployments
- Preserve existing local development workflow

**Non-Goals:**
- Database migration (using existing Firestore setup)
- Custom domain setup (use default Cloud Run domain)
- Authentication/authorization (keep API public)
- Multi-region deployment (single region)

## Decisions

### 1. Backend: Python base image
**Decision**: Use `python:3.13-slim` instead of `python:3.13`
**Rationale**: Smaller image size (~150MB vs ~1GB), faster deployments
**Alternative considered**: Alpine-based images had compatibility issues with some Python packages

### 2. Backend: Uvicorn with multiple workers
**Decision**: Use `uvicorn --workers 4` in production
**Rationale**: Cloud Run handles concurrency; multiple workers improve throughput
**Alternative**: Single worker sufficient for low traffic; scale up workers before scaling instances

### 3. Frontend: Cloud Run static vs Cloud Storage
**Decision**: Use Cloud Run with nginx-static sidecar for simplicity
**Rationale**: Single deployment pipeline for both services, simpler CI/CD
**Alternative considered**: Cloud Storage + CDN cheaper for high traffic but adds complexity

### 4. CI/CD: GitHub Actions over Cloud Build
**Decision**: Use GitHub Actions with `google-github-actions/auth`
**Rationale**: Open source, already using GitHub, easier to debug
**Alternative considered**: Cloud Build triggered by GitHub pushes (more GCP-native)

## Risks / Trade-offs

- **[Risk] Cold starts**: Cloud Run may have latency on first request after idle
  - **Mitigation**: Set `min-instances: 1` for backend (higher cost, consistent performance)
  
- **[Risk] Build time**: Python dependency installation can be slow
  - **Mitigation**: Use Docker layer caching in GitHub Actions

- **[Risk] CORS in production**: May need adjustment for production domain
  - **Mitigation**: Pass `ALLOWED_ORIGINS` env var; default allows localhost for dev

## Migration Plan

1. **Create Dockerfile** for backend with multi-stage build
2. **Create nginx.conf** for frontend static serving  
3. **Create GitHub workflow** `.github/workflows/deploy.yml`
4. **Add GCP secrets** to GitHub repository secrets
5. **First deployment**: Manual trigger to verify
6. **Enable automatic deployments**: Push to main branch triggers deploy

## Open Questions

- Should frontend and backend share one Cloud Run service or be separate?
- What GCP region to deploy to? (default: us-central1)
- Need to configure custom domain or use default *.run.app domain?