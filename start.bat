@echo off
REM Brain Tumor Segmentation - Windows Startup Script
REM Runs both backend (FastAPI) and frontend (React/Vite) concurrently

echo ==========================================
echo   Brain Tumor Segmentation System
echo   Starting services...
echo ==========================================

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

REM Detect Python (prefer python.exe, fallback to py launcher)
set "PYTHON_CMD="
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=py"
    )
)

if "%PYTHON_CMD%"=="" (
    echo Error: Python is not installed or not available on PATH.
    echo.
    echo Fix:
    echo   - Install Python 3.10+ from https://www.python.org/downloads/windows/
    echo   - During install, enable: "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

REM Setup Backend
echo.
echo [1/4] Setting up backend...
cd /d "%BACKEND_DIR%"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
echo Installing backend dependencies...
python -m pip install -r requirements.txt --quiet

REM Setup Frontend
echo.
echo [2/4] Setting up frontend...
cd /d "%FRONTEND_DIR%"

REM Install frontend dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start Backend in new window
echo.
echo [3/4] Starting backend server...
cd /d "%BACKEND_DIR%"
start "Backend - FastAPI" cmd /k "call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo.
echo [4/4] Starting frontend server...
cd /d "%FRONTEND_DIR%"
start "Frontend - Vite" cmd /k "npm run dev"

echo.
echo ==========================================
echo   All services are running!
echo ==========================================
echo   Backend API:  http://localhost:8000
echo   Frontend UI:  http://localhost:5173
echo   API Docs:     http://localhost:8000/docs
echo ==========================================
echo.
echo Close the terminal windows to stop services.
pause
