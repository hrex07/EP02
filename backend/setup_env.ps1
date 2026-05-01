# Setup Environment Variables for Paciência Backend
$env:GOOGLE_CLOUD_PROJECT = "ipt-master"
$env:FIRESTORE_DATABASE = "main"
$env:ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
$env:API_500_INCLUIR_TRACO_NO_JSON = "1"

Write-Host "✅ Environment variables set for this session." -ForegroundColor Green
Write-Host "Note: To make these permanent on Windows, use [System.Environment]::SetEnvironmentVariable('NAME', 'VALUE', 'User')" -ForegroundColor Yellow
