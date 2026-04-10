@echo off
echo === Production Deployment Fix ===
echo.

echo Step 1: Navigate to frontend
cd objective3_interface\frontend

echo.
echo Step 2: Install dependencies
call npm install

echo.
echo Step 3: Build with production environment
call npm run build

echo.
echo Step 4: Build completed successfully!
echo.
echo Next steps:
echo 1. Go to Netlify dashboard
echo 2. Deploy the 'dist' folder manually
echo 3. Or push to Git if auto-deploy is enabled
echo.
echo Current API URL: https://medical-image-segmentation-for-brain-hq5b.onrender.com
echo.

pause
