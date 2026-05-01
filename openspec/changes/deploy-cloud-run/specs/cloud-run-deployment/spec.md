## ADDED Requirements

### Requirement: Docker container configuration
The system SHALL provide a Dockerfile for the FastAPI backend that builds a production-ready container image.

#### Scenario: Dockerfile builds successfully
- **WHEN** `docker build` is run from the project root
- **THEN** a container image is created with Python 3.13-slim, dependencies installed, and FastAPI running on port 8000

#### Scenario: Container runs on Cloud Run
- **WHEN** the container image is deployed to Cloud Run with port 8000
- **THEN** the API responds at the Cloud Run service URL

### Requirement: CI/CD pipeline for automated deployments
The system SHALL provide a GitHub Actions workflow that automatically deploys to Cloud Run on changes to main branch.

#### Scenario: Push to main triggers deployment
- **WHEN** code is pushed to the main branch
- **THEN** GitHub Actions builds the container, pushes to GCR/Artifact Registry, and deploys to Cloud Run

#### Scenario: Deployment status is visible
- **WHEN** a deployment completes
- **THEN** GitHub Actions shows success/failure status with link to Cloud Run service

### Requirement: Environment variable configuration
The system SHALL support environment variables for Cloud Run deployment including Firestore settings and CORS origins.

#### Scenario: Environment variables are passed to container
- **WHEN** Cloud Run service is configured with environment variables
- **THEN** the FastAPI application reads and uses these values at runtime