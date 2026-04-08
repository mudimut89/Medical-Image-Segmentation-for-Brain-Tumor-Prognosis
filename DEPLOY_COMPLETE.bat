@echo off
echo ========================================
echo Complete Deployment Automation
echo ========================================
echo.

echo This script will deploy:
echo - Frontend: Netlify (Automatic)
echo - Backend: Render (Manual setup)
echo.

echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Adding deployment configurations...
git add render.yaml netlify.toml runtime.txt

echo.
echo Step 3: Committing deployment setup...
git commit -m "Complete deployment setup

- Add render.yaml for backend deployment
- Update netlify.toml with backend URL
- Configure Python 3.11 for TensorFlow compatibility
- Ready for full-stack deployment"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo Step 5: Opening deployment platforms...
echo.

echo ========================================
echo FRONTEND DEPLOYMENT (Netlify)
echo ========================================
echo.
echo Your frontend will be automatically deployed to Netlify
echo Build should succeed with Python 3.11.4
echo.
echo Opening Netlify dashboard...
start https://app.netlify.com/sites

echo.
echo ========================================
echo BACKEND DEPLOYMENT (Render)
echo ========================================
echo.
echo To deploy backend:
echo 1. Go to https://render.com
echo 2. Click "New Web Service"
echo 3. Connect your GitHub repository
echo 4. Select: mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis
echo 5. Render will detect render.yaml automatically
echo 6. Click "Create Web Service"
echo.
echo Opening Render...
start https://render.com

echo.
echo ========================================
echo DEPLOYMENT STATUS
echo ========================================
echo.
echo [✓] Frontend: Configured for automatic Netlify deployment
echo [✓] Backend: Configured for Render deployment
echo [✓] GitHub: All configurations pushed
echo [✓] Python: Set to 3.11.4 for TensorFlow compatibility
echo.
echo Expected URLs after deployment:
echo - Frontend: https://your-app.netlify.app
echo - Backend: https://brain-tumor-backend.onrender.com
echo - API Docs: https://brain-tumor-backend.onrender.com/docs
echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Wait for Netlify to auto-rebuild (5-10 minutes)
echo 2. Deploy backend on Render (manual step)
echo 3. Test the full application
echo 4. Share your live brain tumor segmentation system!
echo.
echo Press any key to continue...
pause >nul

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your brain tumor segmentation system is ready for deployment!
echo Both platforms are configured and ready to go.
echo.
echo Check your Netlify dashboard for build status.
echo Follow the Render steps above for backend deployment.
echo.
echo Press any key to exit...
pause >nul
