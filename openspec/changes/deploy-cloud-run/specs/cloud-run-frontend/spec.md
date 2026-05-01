## ADDED Requirements

### Requirement: Frontend static asset serving
The system SHALL serve the React frontend static files alongside the backend API.

#### Scenario: Frontend builds to static assets
- **WHEN** `npm run build` is run in the frontend directory
- **THEN** static assets are generated in the dist/ directory

#### Scenario: Frontend is accessible in production
- **WHEN** the frontend is deployed to Cloud Run or Cloud Storage
- **THEN** users can access the React application via browser

### Requirement: API endpoint configuration for production
The system SHALL configure the frontend to point to the production API endpoint.

#### Scenario: Production API URL is configured
- **WHEN** the application runs in production
- **THEN** API calls go to the Cloud Run service URL instead of localhost

### Requirement: CORS configuration allows production origins
The system SHALL allow CORS requests from the production frontend domain.

#### Scenario: Production origin is allowed
- **WHEN** browser makes request from production domain
- **THEN** CORS is not blocked by the backend