# Free Deployment Platforms for Brain Tumor Segmentation System

## **Top Free Deployment Options**

### **1. Vercel (Frontend) + Railway (Backend) - RECOMMENDED**
**Best for modern web applications**

#### **Frontend Deployment (Vercel)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd objective3_interface/frontend
vercel --prod

# Benefits:
- Free SSL certificates
- Automatic HTTPS
- Global CDN
- GitHub integration
- Custom domains
```

#### **Backend Deployment (Railway)**
```bash
# Create railway.json
echo '{"build": {"builder": "NIXPACKS"}}' > railway.json

# Deploy to Railway
# Connect your GitHub repository
# Automatic deployment from main branch

# Benefits:
- Free tier: $5/month credit
- PostgreSQL database included
- Automatic SSL
- Easy GitHub integration
```

---

### **2. Netlify (Frontend) + Render (Backend)**
**Great for static frontend + API backend**

#### **Frontend Deployment (Netlify)**
```bash
# Build frontend
cd objective3_interface/frontend
npm run build

# Deploy to Netlify
# Drag and drop dist folder to netlify.com
# Or use CLI: npm install -g netlify-cli

# Benefits:
- Free SSL certificates
- Form handling
- Split testing
- Rollbacks
```

#### **Backend Deployment (Render)**
```bash
# Create render.yaml
cat > render.yaml << EOF
services:
  - type: web
    name: brain-tumor-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PORT
        value: 10000
EOF

# Benefits:
- Free tier available
- PostgreSQL database
- Automatic SSL
- GitHub integration
```

---

### **3. GitHub Pages (Frontend) + PythonAnywhere (Backend)**
**Completely free option**

#### **Frontend Deployment (GitHub Pages)**
```bash
# Build frontend
cd objective3_interface/frontend
npm run build

# Create gh-pages branch
git checkout --orphan gh-pages
git add dist
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages

# Enable GitHub Pages in repository settings
# Benefits:
- Completely free
- GitHub integration
- Custom domains
```

#### **Backend Deployment (PythonAnywhere)**
```bash
# Sign up at pythonanywhere.com
# Create Web App
# Upload backend code
# Install dependencies
# Configure WSGI

# Benefits:
- Free tier available
- Easy Python deployment
- Built-in database
```

---

### **4. Firebase Hosting (Frontend) + Heroku (Backend)**
**Google ecosystem option**

#### **Frontend Deployment (Firebase)**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Deploy
firebase deploy --only hosting

# Benefits:
- Free SSL
- Global CDN
- Easy deployment
- Google integration
```

#### **Backend Deployment (Heroku)**
```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Create requirements.txt
pip freeze > requirements.txt

# Deploy to Heroku
heroku create your-app-name
git push heroku main

# Benefits:
- Free tier (550 hours/month)
- PostgreSQL add-on
- Easy deployment
```

---

### **5. Surge.sh (Frontend) + Glitch (Backend)**
**Quick and easy deployment**

#### **Frontend Deployment (Surge.sh)**
```bash
# Install Surge
npm install -g surge

# Build and deploy
cd objective3_interface/frontend
npm run build
cd dist
surge --domain brain-tumor.surge.sh

# Benefits:
- Completely free
- Custom domains
- Instant deployment
```

#### **Backend Deployment (Glitch)**
```bash
# Go to glitch.com
# Create new project
# Import from GitHub
# Remix and configure

# Benefits:
- Free hosting
- Live collaboration
- Easy setup
```

---

### **6. Vercel Full Stack**
**Deploy both frontend and backend together**

#### **Unified Deployment**
```bash
# Create vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "objective3_interface/frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    },
    {
      "src": "objective3_interface/backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/objective3_interface/backend/main.py" },
    { "src": "/(.*)", "dest": "/objective3_interface/frontend/dist/$1" }
  ]
}
EOF

# Deploy
vercel --prod

# Benefits:
- Single platform for both
- Free SSL
- Global CDN
- Serverless functions
```

---

### **7. Netlify Functions + Backend**
**Serverless backend option**

#### **Frontend with Serverless Functions**
```bash
# Create netlify/functions/api.py
# Move backend code to serverless function

# netlify.toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

# Benefits:
- Free serverless functions
- No backend server needed
- Auto-scaling
```

---

## **Platform Comparison**

| Platform | Free Tier | Frontend | Backend | Database | SSL | Custom Domain |
|----------|-----------|----------|---------|----------|-----|--------------|
| **Vercel + Railway** | $5/mo credit | Vercel | Railway | PostgreSQL | Yes | Yes |
| **Netlify + Render** | Unlimited | Netlify | Render | PostgreSQL | Yes | Yes |
| **GitHub Pages + PythonAnywhere** | Unlimited | GitHub Pages | PythonAnywhere | SQLite | Yes | Yes |
| **Firebase + Heroku** | 550h/mo | Firebase | Heroku | PostgreSQL | Yes | Yes |
| **Surge + Glitch** | Unlimited | Surge | Glitch | SQLite | Yes | Yes |
| **Vercel Full Stack** | $5/mo credit | Vercel | Vercel | External | Yes | Yes |

## **Recommended Setup**

### **Option 1: Vercel + Railway (Best Overall)**
```bash
# Frontend to Vercel
cd objective3_interface/frontend
npm run build
vercel --prod

# Backend to Railway
# Connect GitHub repo to Railway
# Automatic deployment
```

### **Option 2: Netlify + Render (Easy Setup)**
```bash
# Frontend to Netlify
cd objective3_interface/frontend
npm run build
# Deploy dist folder to Netlify

# Backend to Render
# Create render.yaml
# Connect GitHub repo
```

### **Option 3: GitHub Pages + PythonAnywhere (Completely Free)**
```bash
# Frontend to GitHub Pages
cd objective3_interface/frontend
npm run build
git checkout --orphan gh-pages
git add dist
git commit -m "Deploy"
git push origin gh-pages

# Backend to PythonAnywhere
# Manual upload and configuration
```

## **Step-by-Step: Vercel + Railway Setup**

### **Step 1: Deploy Frontend to Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy frontend
cd objective3_interface/frontend
vercel --prod

# Follow prompts to:
# - Link to existing project
# - Confirm settings
# - Deploy to production
```

### **Step 2: Deploy Backend to Railway**
```bash
# Create railway.json
echo '{"build": {"builder": "NIXPACKS"}}' > railway.json

# Push to GitHub (if not already)
git add .
git commit -m "Ready for Railway deployment"
git push origin main

# Go to railway.app
# - Click "Deploy from GitHub"
# - Select your repository
# - Configure environment variables
# - Deploy
```

### **Step 3: Configure Frontend to Call Backend**
```javascript
// In objective3_interface/frontend/src/api/config.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend.railway.app' 
  : 'http://localhost:8000';

export const API_URL = API_BASE_URL;
```

### **Step 4: Update Environment Variables**
```bash
# Railway environment variables
DATABASE_URL=postgresql://postgres:password@localhost:5432/brain_tumor
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key
```

## **Step-by-Step: Netlify + Render Setup**

### **Step 1: Deploy Frontend to Netlify**
```bash
# Build frontend
cd objective3_interface/frontend
npm run build

# Deploy to Netlify
# Option 1: Drag and drop dist folder
# Option 2: Use Netlify CLI
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### **Step 2: Deploy Backend to Render**
```bash
# Create render.yaml
cat > render.yaml << EOF
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
EOF

# Push to GitHub
git add render.yaml
git commit -m "Add Render configuration"
git push origin main

# Go to render.com
# - Connect GitHub repository
# - Create new web service
# - Auto-deploy from main branch
```

## **Free Platform Limitations**

### **Common Limitations**
- **Usage limits**: Most have monthly limits
- **Cold starts**: Serverless functions may have delays
- **Database limits**: Free databases have size limits
- **Custom domains**: Some require paid plans
- **Support**: Community support only

### **How to Stay Within Free Limits**
- **Optimize images**: Compress MRI images
- **Cache responses**: Use Redis caching
- **Monitor usage**: Check platform dashboards
- **Database cleanup**: Regular maintenance

## **Migration to Paid Plans**

### **When to Upgrade**
- High traffic (>1000 users/month)
- Need custom domains
- Require priority support
- Need more database storage

### **Typical Costs**
- **Vercel Pro**: $20/month
- **Railway**: $5-20/month
- **Netlify**: $19/month
- **Render**: $7-25/month

## **Quick Deployment Scripts**

### **Vercel Deployment Script**
```bash
#!/bin/bash
echo "Deploying to Vercel + Railway..."

# Deploy frontend
cd objective3_interface/frontend
npm run build
vercel --prod

echo "Frontend deployed to Vercel!"
echo "Backend: Deploy to Railway manually"
```

### **Netlify Deployment Script**
```bash
#!/bin/bash
echo "Deploying to Netlify + Render..."

# Deploy frontend
cd objective3_interface/frontend
npm run build
netlify deploy --prod --dir=dist

echo "Frontend deployed to Netlify!"
echo "Backend: Deploy to Render manually"
```

## **Recommendation**

### **For Your Project**
**Vercel + Railway** is the best choice because:
- Modern tech stack support
- Easy GitHub integration
- Good free tier
- Automatic SSL
- Professional appearance

### **Alternative**
**Netlify + Render** if you prefer:
- Simpler setup
- Better documentation
- More generous free tier

---

**Choose the platform that best fits your needs and budget! All options will give you a professional, deployed application.**
