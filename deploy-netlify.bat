@echo off
echo ========================================
echo Netlify Deployment - Brain Tumor Segmentation
echo ========================================
echo.

echo This will deploy your frontend to Netlify (FREE)
echo Backend will need to be deployed separately
echo.

echo Step 1: Installing Netlify CLI...
npm install -g netlify-cli

echo.
echo Step 2: Building frontend...
cd objective3_interface\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo Building for production...
npm run build

echo.
echo Step 3: Deploying to Netlify...
echo Please login to Netlify when prompted...
netlify login

echo.
echo Deploying frontend...
netlify deploy --prod --dir=dist

echo.
echo ========================================
echo Frontend Deployment Complete!
echo ========================================
echo.
echo Your frontend is now live on Netlify!
echo.
echo Next Steps:
echo 1. Deploy backend to Render or Railway
echo 2. Update API URL in frontend code
echo 3. Test the full application
echo.
echo Backend Deployment Options:
echo - Render: https://render.com (Free tier available)
echo - Railway: https://railway.app ($5 credit)
echo - PythonAnywhere: https://pythonanywhere.com (Free tier)
echo.
echo Press any key to open Netlify dashboard...
pause >nul
start https://app.netlify.com/account/sites

echo Press any key to open Render for backend deployment...
pause >nul
start https://render.com

echo.
echo Your Netlify site URL will be shown above.
echo Save it for backend configuration!
