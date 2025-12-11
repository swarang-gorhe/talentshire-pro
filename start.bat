@echo off
REM Talentshire Platform Startup Script for Windows
REM This script starts both backend and frontend services

echo.
echo ╔═══════════════════════════════════════╗
echo ║  Talentshire Platform Startup        ║
echo ║  Full-Stack Assessment System        ║
echo ╚═══════════════════════════════════════╝
echo.

REM Colors using findstr
setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+ from nodejs.org
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Start Backend
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 Starting Backend (FastAPI on port 8000)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r backend\requirements.txt

REM Start backend in new window
cd backend
echo ✅ Backend starting...
echo    API Documentation: http://localhost:8000/docs
echo    Health Check: http://localhost:8000/health
start "Talentshire Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
cd ..

timeout /t 2 /nobreak

REM Start Frontend
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 Starting Frontend (Vite on port 8080)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ⚠️  Dependencies not installed. Running npm install...
    cd frontend
    npm install
    cd ..
)

cd frontend
echo ✅ Frontend starting...
echo    Application: http://localhost:8080
start "Talentshire Frontend" npm run dev -- --host 0.0.0.0 --port 8080
cd ..

timeout /t 3 /nobreak

REM Database information
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🗄️  Database Information
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PostgreSQL Connection:
echo   Host: localhost
echo   Port: 5432
echo   Database: talentshire
echo   Username: talentshire
echo   Password: talentshire123
echo.
echo ⚠️  Make sure PostgreSQL is running before accessing the app
echo.

REM Show summary
echo.
echo ╔═══════════════════════════════════════╗
echo ║       ✅ Platform Ready!              ║
echo ╚═══════════════════════════════════════╝
echo.
echo 📍 Services Running:
echo    🔹 Backend API:    http://localhost:8000
echo    🔹 API Docs:       http://localhost:8000/docs
echo    🔹 Frontend:       http://localhost:8080
echo.
echo 📍 Default Credentials:
echo    🔹 Admin Email:    admin@talentshire.com
echo    🔹 Candidate Email: candidate@talentshire.com
echo.
echo 📍 Documentation:
echo    🔹 README:         README.md
echo    🔹 Structure:      REPOSITORY_STRUCTURE.md
echo.
echo ℹ️  Services running in separate windows
echo.

pause
