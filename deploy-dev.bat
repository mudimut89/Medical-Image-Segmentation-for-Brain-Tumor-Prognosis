@echo off
echo ========================================
echo Brain Tumor Segmentation - Development
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "medseg_env\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv medseg_env
)

REM Activate virtual environment
echo Activating virtual environment...
call medseg_env\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
cd objective3_interface\backend
pip install -r requirements.txt

REM Start backend in background
echo Starting backend server...
start "Backend Server" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Install frontend dependencies
echo Installing frontend dependencies...
cd ..\..\objective3_interface\frontend
call npm install

REM Start frontend
echo Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Development Server Started!
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
