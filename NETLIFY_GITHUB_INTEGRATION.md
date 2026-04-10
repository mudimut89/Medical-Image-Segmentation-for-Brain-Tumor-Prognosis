# Netlify GitHub Integration Setup

## **Option 3: GitHub Integration (Automatic Deployment)**

### **Step-by-Step Setup**

#### **Step 1: Add Netlify Configuration to Your Repository**
```bash
# The netlify.toml file has been added to your repository
# This tells Netlify how to build your site
```

#### **Step 2: Push Configuration to GitHub**
```bash
git commit -m "Add Netlify configuration for automatic deployment"
git push origin main
```

#### **Step 3: Connect Netlify to GitHub**

1. **Go to**: https://netlify.com
2. **Sign up** or **Log in** to your account
3. **Click**: "Add new site" > "Import an existing project"
4. **Select**: "GitHub" (authorize if needed)
5. **Choose repository**: `mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis`

#### **Step 4: Configure Build Settings**
```
Build settings (Netlify will detect from netlify.toml):
- Publish directory: objective3_interface/frontend/dist
- Build command: cd objective3_interface/frontend && npm install && npm run build
- Node version: 18
```

#### **Step 5: Deploy Site**
1. **Click**: "Deploy site"
2. **Wait** for build to complete (2-3 minutes)
3. **Your site is LIVE!**

---

## **Automatic Deployment Features**

### **What Happens Automatically**
- **Build triggers**: Every push to main branch
- **Preview deployments**: Pull requests get preview URLs
- **Rollbacks**: Easy rollback to previous versions
- **Environment variables**: Different settings per branch
- **Custom domains**: Automatic SSL setup

### **Branch Deployments**
- **Main branch**: Production site
- **Feature branches**: Preview URLs
- **Pull requests**: Automatic preview builds

---

## **Complete Setup Process**

### **Step 1: Repository Ready**
```bash
# Your repository now includes:
- netlify.toml (build configuration)
- All source code
- GitHub integration ready
```

### **Step 2: Netlify Setup**
1. **Open**: https://app.netlify.com/start
2. **Click**: "GitHub" 
3. **Authorize**: Netlify to access your repositories
4. **Select**: `mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis`

### **Step 3: Build Configuration**
Netlify will automatically detect:
```
Build command: cd objective3_interface/frontend && npm install && npm run build
Publish directory: objective3_interface/frontend/dist
```

### **Step 4: Environment Variables**
Add these in Netlify dashboard:
```
API_URL=https://your-backend-url.onrender.com
NODE_ENV=production
```

### **Step 5: Deploy**
1. **Click**: "Deploy site"
2. **Wait** for build
3. **Get your URL**: `https://your-app-name.netlify.app`

---

## **Backend Deployment (Separate)**

### **Deploy Backend to Render**
1. **Go to**: https://render.com
2. **Sign up** and connect GitHub
3. **Select**: Same repository
4. **Configure Web Service**:
   - **Name**: brain-tumor-backend
   - **Root Directory**: `objective3_interface/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Deploy**

### **Update Netlify Configuration**
After backend is deployed, update `netlify.toml`:
```toml
[[redirects]]
  from = "/api/*"
  to = "https://brain-tumor-backend.onrender.com/api/:splat"
  status = 200
```

---

## **Benefits of GitHub Integration**

### **Automatic Features**
- **Continuous Deployment**: Every push triggers a build
- **Pull Request Previews**: Test changes before merging
- **Rollback Capability**: Easy rollback to previous versions
- **Branch Environments**: Different settings per branch
- **Build Logs**: Detailed build information

### **Workflow Integration**
- **GitHub Actions**: Can work alongside Netlify
- **Issue Tracking**: Link builds to GitHub issues
- **Team Collaboration**: Multiple developers can deploy
- **Status Checks**: Build status in GitHub PRs

---

## **Advanced Configuration**

### **Environment Variables**
```bash
# In Netlify dashboard: Site settings > Build & deploy > Environment
API_URL=https://brain-tumor-backend.onrender.com
NODE_ENV=production
REACT_APP_API_URL=https://brain-tumor-backend.onrender.com
```

### **Custom Headers**
```toml
# Already in netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
```

### **Plugin Configuration**
```toml
# Add to netlify.toml for plugins
[[plugins]]
  package = "@netlify/plugin-lighthouse"
  [plugins.inputs]
    output_path = "lighthouse.html"
```

---

## **Troubleshooting**

### **Build Fails**
1. **Check build logs** in Netlify dashboard
2. **Verify netlify.toml** syntax
3. **Check Node version** compatibility
4. **Ensure dependencies** are in package.json

### **API Calls Fail**
1. **Update API URL** in Netlify environment variables
2. **Check CORS settings** in backend
3. **Verify backend deployment** status

### **Redirect Issues**
1. **Check netlify.toml** redirect rules
2. **Test API endpoints** directly
3. **Verify build output** structure

---

## **Next Steps After Setup**

### **1. Deploy Backend**
- Set up Render or Railway
- Get backend URL
- Update netlify.toml

### **2. Test Full Application**
- Upload MRI images
- Test tumor detection
- Verify API connectivity

### **3. Custom Domain (Optional)**
- Add custom domain in Netlify
- Update DNS settings
- Verify SSL certificate

### **4. Team Collaboration**
- Invite team members to Netlify
- Set up branch protections
- Configure deployment permissions

---

## **Quick Start Commands**

### **Initial Setup**
```bash
# Push configuration to GitHub
git add netlify.toml
git commit -m "Add Netlify configuration"
git push origin main
```

### **Update Configuration**
```bash
# After backend deployment
git add netlify.toml
git commit -m "Update backend URL"
git push origin main
```

---

## **Success Metrics**

### **What You'll Have**
- **Automatic deployments** on every push
- **Preview URLs** for pull requests
- **Rollback capability** for safety
- **Environment separation** (dev/prod)
- **Team collaboration** features

### **Professional Setup**
- **CI/CD pipeline** without extra tools
- **Zero-downtime deployments**
- **Global CDN** distribution
- **Automatic SSL** certificates
- **Custom domain** support

---

## **Final Result**

### **Your Live Application**
- **Frontend**: `https://your-app.netlify.app`
- **Backend**: `https://brain-tumor-backend.onrender.com`
- **Repository**: Automatic deployment from GitHub
- **Team**: Collaborative development workflow

### **Deployment Workflow**
1. **Push code** to GitHub
2. **Netlify builds** automatically
3. **Site updates** instantly
4. **Team can test** via preview URLs

---

**Your brain tumor segmentation system now has professional CI/CD with automatic deployments!**
