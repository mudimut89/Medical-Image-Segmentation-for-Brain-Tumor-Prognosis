@echo off
echo ========================================
echo Brain Tumor Segmentation Deployment
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo Docker is installed. Starting deployment...
echo.

REM Build and start services
echo Building Docker images...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo Checking service status...
timeout /t 10 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Access your application:
echo - Frontend: http://localhost:80
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo.
echo Press any key to open the application in your browser...
pause >nul
start http://localhost:80
