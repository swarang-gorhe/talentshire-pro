@echo off
REM Talentshire - Complete Startup Script for Windows
REM This script starts both frontend and backend automatically

setlocal enabledelayedexpansion

REM Define colors for output
set "SUCCESS=[SUCCESS]"
set "ERROR=[ERROR]"
set "INFO=[INFO]"

echo.
echo =====================================
echo   TALENTSHIRE - STARTUP LAUNCHER
echo =====================================
echo.

REM Get project root directory
set "PROJECT_ROOT=C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main"

REM Check if project directory exists
if not exist "%PROJECT_ROOT%" (
    echo %ERROR% Project directory not found: %PROJECT_ROOT%
    echo Please update the PROJECT_ROOT path in this script.
    pause
    exit /b 1
)

echo %INFO% Project root: %PROJECT_ROOT%
echo.

REM Check prerequisites
echo %INFO% Checking prerequisites...

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo %ERROR% Node.js is not installed or not in PATH
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo %ERROR% Python is not installed or not in PATH
    echo Please install Python 3.11+ from: https://www.python.org/
    pause
    exit /b 1
)

REM Check if PostgreSQL is running
powershell -Command "Get-Process -Name postgres -ErrorAction SilentlyContinue | Select-Object -First 1 >nul"
if errorlevel 1 (
    echo %ERROR% PostgreSQL is not running!
    echo Please start PostgreSQL service before proceeding.
    echo.
    echo To start PostgreSQL on Windows:
    echo   1. Open Services (services.msc)
    echo   2. Find "PostgreSQL" service
    echo   3. Right-click and select "Start"
    echo.
    echo Or run: pg_ctl -D "C:\Program Files\PostgreSQL\data" start
    echo.
    pause
    exit /b 1
) else (
    echo %SUCCESS% PostgreSQL is running
)

REM Check if MongoDB is running
powershell -Command "Get-Process -Name mongod -ErrorAction SilentlyContinue | Select-Object -First 1 >nul"
if errorlevel 1 (
    echo %ERROR% MongoDB is not running!
    echo Please start MongoDB service before proceeding.
    echo.
    echo To start MongoDB on Windows:
    echo   1. Open Services (services.msc)
    echo   2. Find "MongoDB" service
    echo   3. Right-click and select "Start"
    echo.
    echo Or run: mongod --dbpath "C:\data\db"
    echo.
    pause
    exit /b 1
) else (
    echo %SUCCESS% MongoDB is running
)

echo.
echo %SUCCESS% All prerequisites are installed!
echo.
echo =====================================
echo   STARTING SERVICES
echo =====================================
echo.

REM Open new terminal windows for frontend and backend

REM Terminal 1: Frontend
echo %INFO% Starting Frontend (Vite) on http://localhost:8080
cd /d "%PROJECT_ROOT%"
start "TALENTSHIRE - FRONTEND" cmd /k "npm run dev"

REM Wait a moment before starting backend
timeout /t 3 /nobreak

REM Terminal 2: Backend
echo %INFO% Starting Backend (FastAPI) on http://localhost:8000
cd /d "%PROJECT_ROOT%\backend"
start "TALENTSHIRE - BACKEND" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment before showing final message
timeout /t 3 /nobreak

echo.
echo =====================================
echo   ✅ STARTUP COMPLETE!
echo =====================================
echo.
echo Frontend is available at:  http://localhost:8080/
echo Backend is available at:   http://localhost:8000/
echo API Docs (Swagger) at:     http://localhost:8000/docs
echo.
echo Default Login Credentials:
echo   Email: test@example.com
echo   Token: test_token_123
echo.
echo PostgreSQL Connection:
echo   Host: localhost
echo   Port: 5432
echo   Username: postgres
echo   Password: Admin@123
echo   Database: talentshire
echo.
echo MongoDB Connection:
echo   URL: mongodb://127.0.0.1:27017
echo   Database: talentshire
echo.
echo =====================================
echo.
pause
