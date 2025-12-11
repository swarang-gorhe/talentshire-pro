# Talentshire - Complete Startup Script for PowerShell
# Run as: powershell -ExecutionPolicy Bypass -File START_ALL.ps1

param(
    [switch]$SkipChecks = $false
)

# Colors for output
$Success = "Green"
$Error = "Red"
$Warning = "Yellow"
$Info = "Cyan"

# Banner
Write-Host "`n" -ForegroundColor $Info
Write-Host "=====================================" -ForegroundColor $Info
Write-Host "   TALENTSHIRE - STARTUP LAUNCHER  " -ForegroundColor $Info
Write-Host "=====================================" -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

# Project root
$ProjectRoot = "C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main"
$BackendPath = Join-Path $ProjectRoot "backend"

# Check if project exists
if (-not (Test-Path $ProjectRoot)) {
    Write-Host "[ERROR] Project directory not found: $ProjectRoot" -ForegroundColor $Error
    Write-Host "Please update the ProjectRoot path in this script." -ForegroundColor $Error
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Project root: $ProjectRoot" -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

# Prerequisites Check
if (-not $SkipChecks) {
    Write-Host "[INFO] Checking prerequisites..." -ForegroundColor $Info
    
    # Check Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor $Error
        Write-Host "Please install from: https://nodejs.org/" -ForegroundColor $Error
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor $Error
        Write-Host "Please install Python 3.11+ from: https://www.python.org/" -ForegroundColor $Error
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check PostgreSQL
    $PostgresProcess = Get-Process -Name postgres -ErrorAction SilentlyContinue
    if (-not $PostgresProcess) {
        Write-Host "[ERROR] PostgreSQL is not running!" -ForegroundColor $Error
        Write-Host "`nTo start PostgreSQL:" -ForegroundColor $Warning
        Write-Host "  1. Open Services (services.msc)" -ForegroundColor $Warning
        Write-Host "  2. Find 'PostgreSQL' service" -ForegroundColor $Warning
        Write-Host "  3. Right-click and select 'Start'" -ForegroundColor $Warning
        Write-Host "`nOr run: pg_ctl -D `"C:\Program Files\PostgreSQL\data`" start" -ForegroundColor $Warning
        Write-Host "`n" -ForegroundColor $Info
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        Write-Host "[SUCCESS] PostgreSQL is running" -ForegroundColor $Success
    }
    
    # Check MongoDB
    $MongoProcess = Get-Process -Name mongod -ErrorAction SilentlyContinue
    if (-not $MongoProcess) {
        Write-Host "[ERROR] MongoDB is not running!" -ForegroundColor $Error
        Write-Host "`nTo start MongoDB:" -ForegroundColor $Warning
        Write-Host "  1. Open Services (services.msc)" -ForegroundColor $Warning
        Write-Host "  2. Find 'MongoDB' service" -ForegroundColor $Warning
        Write-Host "  3. Right-click and select 'Start'" -ForegroundColor $Warning
        Write-Host "`nOr run: mongod --dbpath `"C:\data\db`"" -ForegroundColor $Warning
        Write-Host "`n" -ForegroundColor $Info
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        Write-Host "[SUCCESS] MongoDB is running" -ForegroundColor $Success
    }
    
    Write-Host "`n[SUCCESS] All prerequisites are installed!" -ForegroundColor $Success
    Write-Host "`n" -ForegroundColor $Info
}

# Start services
Write-Host "=====================================" -ForegroundColor $Info
Write-Host "   STARTING SERVICES" -ForegroundColor $Info
Write-Host "=====================================" -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

# Start Frontend
Write-Host "[INFO] Starting Frontend (Vite) on http://localhost:8080" -ForegroundColor $Info
$FrontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; npm run dev" -PassThru -WindowStyle Normal

# Wait before starting backend
Start-Sleep -Seconds 3

# Start Backend
Write-Host "[INFO] Starting Backend (FastAPI) on http://localhost:8000" -ForegroundColor $Info
$BackendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendPath'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -WindowStyle Normal

# Wait for services to start
Start-Sleep -Seconds 3

# Display final message
Write-Host "`n" -ForegroundColor $Info
Write-Host "=====================================" -ForegroundColor $Success
Write-Host "   ✅ STARTUP COMPLETE!" -ForegroundColor $Success
Write-Host "=====================================" -ForegroundColor $Success
Write-Host "`n" -ForegroundColor $Info

Write-Host "Frontend is available at:  http://localhost:8080/" -ForegroundColor $Success
Write-Host "Backend is available at:   http://localhost:8000/" -ForegroundColor $Success
Write-Host "API Docs (Swagger) at:     http://localhost:8000/docs" -ForegroundColor $Success
Write-Host "`n" -ForegroundColor $Info

Write-Host "Default Login Credentials:" -ForegroundColor $Warning
Write-Host "  Email: test@example.com" -ForegroundColor $Warning
Write-Host "  Token: test_token_123" -ForegroundColor $Warning
Write-Host "`n" -ForegroundColor $Info

Write-Host "PostgreSQL Connection:" -ForegroundColor $Info
Write-Host "  Host: localhost" -ForegroundColor $Info
Write-Host "  Port: 5432" -ForegroundColor $Info
Write-Host "  Username: postgres" -ForegroundColor $Info
Write-Host "  Password: Admin@123" -ForegroundColor $Info
Write-Host "  Database: talentshire" -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

Write-Host "MongoDB Connection:" -ForegroundColor $Info
Write-Host "  URL: mongodb://127.0.0.1:27017" -ForegroundColor $Info
Write-Host "  Database: talentshire" -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

Write-Host "=====================================" -ForegroundColor $Success
Write-Host "`n" -ForegroundColor $Info

Write-Host "To view logs:" -ForegroundColor $Warning
Write-Host "  Frontend logs are in the FRONTEND terminal" -ForegroundColor $Warning
Write-Host "  Backend logs are in the BACKEND terminal" -ForegroundColor $Warning
Write-Host "`n" -ForegroundColor $Info

Write-Host "To stop services:" -ForegroundColor $Warning
Write-Host "  1. Go to the FRONTEND terminal and press Ctrl+C" -ForegroundColor $Warning
Write-Host "  2. Go to the BACKEND terminal and press Ctrl+C" -ForegroundColor $Warning
Write-Host "`n" -ForegroundColor $Info
