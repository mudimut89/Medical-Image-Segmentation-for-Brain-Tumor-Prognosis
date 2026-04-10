@echo off
echo ========================================
echo Free Platform Deployment Setup
echo ========================================
echo.

echo This script will help you deploy to:
echo - Frontend: Vercel (Free)
echo - Backend: Railway (Free $5/month credit)
echo.

echo Step 1: Installing Vercel CLI...
npm install -g vercel

echo.
echo Step 2: Building frontend...
cd objective3_interface\frontend
npm run build

echo.
echo Step 3: Deploying frontend to Vercel...
vercel --prod

echo.
echo Step 4: Creating Railway configuration...
echo {"build": {"builder": "NIXPACKS"}} > railway.json

echo.
echo ========================================
echo Frontend Deployment Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Go to https://railway.app
echo 2. Click "Deploy from GitHub repo"
echo 3. Select your repository: mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis
echo 4. Configure environment variables:
echo    - DATABASE_URL=postgresql://postgres:password@localhost:5432/brain_tumor
echo    - ENVIRONMENT=production
echo    - SECRET_KEY=your-secret-key
echo 5. Click "Deploy"
echo.
echo Your app will be available at:
echo - Frontend: https://your-app.vercel.app
echo - Backend: https://your-backend.railway.app
echo.
echo Press any key to open Vercel dashboard...
pause >nul
start https://vercel.com/dashboard

echo Press any key to open Railway dashboard...
pause >nul
start https://railway.app/new
