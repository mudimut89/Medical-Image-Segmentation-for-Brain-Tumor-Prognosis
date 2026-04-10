# Netlify Deployment Guide for Brain Tumor Segmentation System

## **Netlify Deployment Options**

### **Option 1: Frontend Only (Recommended)**
Deploy the React frontend to Netlify with backend on a separate platform

### **Option 2: Full Stack with Netlify Functions**
Deploy both frontend and backend using Netlify's serverless functions

---

## **Option 1: Frontend Deployment to Netlify (Easiest)**

### **Step 1: Build Frontend**
```bash
# Navigate to frontend directory
cd objective3_interface/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### **Step 2: Deploy to Netlify**

#### **Method A: Drag and Drop (Easiest)**
1. **Build the frontend** (Step 1)
2. **Go to**: https://netlify.com
3. **Sign up** for free account
4. **Drag and drop** the `dist` folder to the deployment area
5. **Wait for deployment** (usually 1-2 minutes)
6. **Your site is live!**

#### **Method B: Netlify CLI (More Control)**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
cd objective3_interface/frontend
netlify deploy --prod --dir=dist
```

#### **Method C: GitHub Integration (Automatic)**
1. **Connect GitHub** to Netlify
2. **Select your repository**: `mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis`
3. **Configure build settings**:
   - **Build command**: `cd objective3_interface/frontend && npm run build`
   - **Publish directory**: `objective3_interface/frontend/dist`
4. **Deploy site**

### **Step 3: Configure Backend API**
Since the frontend is on Netlify, you need to update the API calls:

```javascript
// In objective3_interface/frontend/src/api/config.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-api-url.com'  // Your backend URL
  : 'http://localhost:8000';

export const API_URL = API_BASE_URL;
```

### **Step 4: Backend Deployment Options**
Choose one of these for your backend:

#### **Option A: Render (Recommended)**
```bash
# Go to https://render.com
# Create new web service
# Connect your GitHub repository
# Configure:
# - Build Command: `pip install -r requirements.txt`
# - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
```

#### **Option B: Railway**
```bash
# Go to https://railway.app
# Deploy from GitHub repo
# Automatic deployment
```

#### **Option C: PythonAnywhere**
```bash
# Go to https://pythonanywhere.com
# Create web app
# Upload backend code
# Configure WSGI
```

---

## **Option 2: Full Stack with Netlify Functions**

### **Step 1: Restructure Project for Netlify Functions**
```bash
# Create netlify directory structure
mkdir -p netlify/functions
mkdir -p netlify/public
```

### **Step 2: Move Frontend to Public Folder**
```bash
# Copy built frontend to public folder
cp -r objective3_interface/frontend/dist/* netlify/public/
```

### **Step 3: Create Backend Function**
```python
# Create netlify/functions/api.py
import json
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add your backend code here
# You'll need to adapt your FastAPI code to work with Netlify functions

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"message": "Brain Tumor Segmentation API"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Process MRI upload here
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "success", "message": "MRI processed"}
        self.wfile.write(json.dumps(response).encode())
```

### **Step 4: Create Netlify Configuration**
```toml
# Create netlify.toml
[build]
  publish = "netlify/public"
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
```

### **Step 5: Deploy Full Stack**
```bash
# Deploy to Netlify
netlify deploy --prod
```

---

## **Step-by-Step: Quick Netlify Deployment**

### **Step 1: Prepare Frontend**
```bash
cd objective3_interface/frontend
npm install
npm run build
```

### **Step 2: Deploy to Netlify**
```bash
# Method 1: Drag and drop
# Go to https://netlify.com
# Drag the `dist` folder to the deploy area

# Method 2: CLI
npm install -g netlify-cli
netlify login
netlify deploy --prod --dir=dist
```

### **Step 3: Get Your Netlify URL**
Your site will be available at:
- `https://amazing-einstein-123456.netlify.app`
- Or your custom domain if you set one up

### **Step 4: Update API Configuration**
```javascript
// Update this in your frontend code
const API_URL = 'https://your-backend-url.com/api';
```

---

## **Netlify Configuration Files**

### **netlify.toml (Advanced Configuration)**
```toml
[build]
  publish = "objective3_interface/frontend/dist"
  command = "cd objective3_interface/frontend && npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[context.production]
  [context.production.environment]
    API_URL = "https://your-backend.com"
```

### **_redirects File (Simple Redirects)**
```
# Create _redirects file in dist folder
/api/*  https://your-backend.com/api/:splat  200
/*      /index.html   200
```

---

## **Environment Variables**

### **Netlify Environment Variables**
```bash
# Set in Netlify dashboard: Site settings > Build & deploy > Environment
API_URL=https://your-backend.com
NODE_ENV=production
```

### **Accessing Environment Variables in React**
```javascript
// In your React app
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

---

## **Custom Domain Setup**

### **Step 1: Add Custom Domain**
1. **Go to**: Netlify dashboard > Site settings > Domain management
2. **Add custom domain**: `yourdomain.com`
3. **Verify domain ownership**

### **Step 2: Update DNS**
```
# Add these DNS records
Type: A
Name: @
Value: 104.198.14.52

Type: CNAME  
Name: www
Value: your-site.netlify.app
```

### **Step 3: SSL Certificate**
- **Automatic**: Netlify provides free SSL
- **Manual**: Upload your own certificate if needed

---

## **Backend Deployment Options**

### **Option 1: Render (Recommended)**
```bash
# Create render.yaml
services:
  - type: web
    name: brain-tumor-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PORT
        value: 10000
      - key: ENVIRONMENT
        value: production
```

### **Option 2: Railway**
```bash
# Create railway.json
{"build": {"builder": "NIXPACKS"}}
```

### **Option 3: PythonAnywhere**
```bash
# Upload to PythonAnywhere
# Configure WSGI file
# Install dependencies
# Start web app
```

---

## **Troubleshooting**

### **Common Issues**

#### **Build Fails**
```bash
# Check build logs in Netlify dashboard
# Common issues:
# - Missing dependencies
# - Build command incorrect
# - Environment variables missing
```

#### **API Calls Fail**
```bash
# Check CORS settings
# Verify backend URL
# Check network tab in browser
```

#### **Static Assets Not Loading**
```bash
# Check file paths
# Verify base URL in React Router
# Check _redirects file
```

### **Debugging Tips**
```bash
# Enable debug mode
REACT_APP_DEBUG=true

# Check Netlify logs
# View function logs in dashboard

# Test locally
netlify dev
```

---

## **Performance Optimization**

### **Image Optimization**
```bash
# Optimize MRI images before upload
# Use WebP format
# Compress images
```

### **Caching**
```toml
# In netlify.toml
[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### **Bundle Size**
```bash
# Analyze bundle size
npm run build --analyze

# Optimize imports
# Use code splitting
```

---

## **Security**

### **CORS Configuration**
```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-site.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Environment Variables**
```bash
# Never commit secrets to Git
# Use Netlify environment variables
# Use HTTPS only
```

---

## **Monitoring and Analytics**

### **Netlify Analytics**
```bash
# Enable in Netlify dashboard
# Site settings > Analytics
# Free tier available
```

### **Error Tracking**
```bash
# Add error tracking
# Use Sentry or similar
# Monitor API errors
```

---

## **Quick Deployment Script**

### **deploy-netlify.bat**
```batch
@echo off
echo ========================================
echo Netlify Deployment
echo ========================================
echo.

echo Step 1: Building frontend...
cd objective3_interface\frontend
npm install
npm run build

echo.
echo Step 2: Deploying to Netlify...
netlify deploy --prod --dir=dist

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your site is live at:
echo https://your-site.netlify.app
echo.
echo Next steps:
echo 1. Deploy backend to Render/Railway
echo 2. Update API URL in frontend
echo 3. Test the application
echo.
echo Press any key to open your site...
pause >nul
start https://your-site.netlify.app
```

---

## **Summary**

### **Recommended Approach**
1. **Frontend**: Netlify (free, easy, professional)
2. **Backend**: Render or Railway (free tier available)
3. **Database**: PostgreSQL (included with backend platform)

### **Benefits**
- **Free hosting**
- **Automatic SSL**
- **Global CDN**
- **Custom domains**
- **Easy deployment**
- **Professional appearance**

### **Next Steps**
1. **Deploy frontend to Netlify**
2. **Deploy backend to Render/Railway**
3. **Update API configuration**
4. **Test the full application**
5. **Set up custom domain (optional)**

---

**Your brain tumor segmentation system will be live on Netlify within minutes!**
