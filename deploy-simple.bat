@echo off
echo ========================================
echo Brain Tumor Segmentation - Simple Deployment
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python from: https://www.python.org/
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv brain_tumor_env

echo Activating virtual environment...
call brain_tumor_env\Scripts\activate.bat

echo Installing backend dependencies...
cd objective3_interface\backend
pip install fastapi uvicorn tensorflow opencv-python numpy pillow python-multipart

echo Starting backend server...
start "Backend Server" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Installing frontend dependencies...
cd ..\..\objective3_interface\frontend
call npm install

echo Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Access your application:
echo - Frontend: http://localhost:5173
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
echo Press any key to open the application in your browser...
pause >nul
start http://localhost:5173
