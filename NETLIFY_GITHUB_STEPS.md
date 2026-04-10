# Netlify GitHub Integration - Step by Step

## **Your Repository is Ready!**

I've already:
- [x] Added `netlify.toml` configuration file
- [x] Pushed it to your GitHub repository
- [x] Your repository is ready for Netlify integration

## **Next Steps - Complete the Setup**

### **Step 1: Go to Netlify**
**Open**: https://app.netlify.com/start

### **Step 2: Connect GitHub**
1. **Click** on "GitHub" (you'll need to authorize Netlify)
2. **Sign in** to your GitHub account if prompted
3. **Allow** Netlify to access your repositories

### **Step 3: Select Your Repository**
1. **Find and select**: `mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis`
2. **Click**: "Import repository"

### **Step 4: Configure Build Settings**
Netlify will automatically detect these settings from your `netlify.toml`:
```
- Publish directory: objective3_interface/frontend/dist
- Build command: cd objective3_interface/frontend && npm install && npm run build
- Node version: 18
```

### **Step 5: Deploy Site**
1. **Click**: "Deploy site"
2. **Wait** 2-3 minutes for the build to complete
3. **Success!** Your site is live

## **What You'll Get**

### **Automatic Deployment URL**
Your site will be available at:
- `https://amazing-einstein-123456.netlify.app`
- (Netlify gives you a random name)

### **Professional Features**
- **Automatic HTTPS** (SSL certificate)
- **Global CDN** (fast loading worldwide)
- **Custom domain** (free setup)
- **Pull request previews**
- **Rollback capability**

## **After Netlify Deployment**

### **Step 6: Deploy Backend to Render**
1. **Go to**: https://render.com
2. **Sign up** and connect GitHub
3. **Select**: Same repository
4. **Configure Web Service**:
   - **Name**: brain-tumor-backend
   - **Root Directory**: `objective3_interface/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Deploy**

### **Step 7: Connect Frontend to Backend**
After your backend is deployed, you'll need to update the API URL.

**Your backend URL will be**: `https://brain-tumor-backend.onrender.com`

**Update the redirect in netlify.toml**:
```toml
[[redirects]]
  from = "/api/*"
  to = "https://brain-tumor-backend.onrender.com/api/:splat"
  status = 200
```

### **Step 8: Test Your Application**
1. **Open your Netlify URL**
2. **Upload an MRI image**
3. **Check if tumor detection works**
4. **Verify API connectivity**

## **Quick Links**

### **Direct Links to Get Started**
- **Netlify Start**: https://app.netlify.com/start
- **Your GitHub Repo**: https://github.com/mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis
- **Render**: https://render.com (for backend)

### **What to Expect**
- **Build Time**: 2-3 minutes
- **Success Page**: Netlify will show your live site
- **Dashboard**: You'll see build logs and site settings

## **Troubleshooting**

### **If Build Fails**
1. **Check build logs** in Netlify dashboard
2. **Verify** the build command is correct
3. **Check** Node.js version compatibility

### **If API Doesn't Work**
1. **Deploy backend first** to Render
2. **Update** the API URL in netlify.toml
3. **Push** the updated configuration

### **If You Need Help**
1. **Check** the detailed guide: `NETLIFY_GITHUB_INTEGRATION.md`
2. **Review** Netlify documentation
3. **Contact** Netlify support

## **Success!**

### **What You'll Have**
- **Live frontend**: Deployed on Netlify
- **Live backend**: Deployed on Render
- **Automatic deployments**: Every push triggers rebuild
- **Professional setup**: CI/CD pipeline
- **Team collaboration**: Multiple developers can deploy

### **Your Live Application**
- **Frontend**: `https://your-app.netlify.app`
- **Backend**: `https://brain-tumor-backend.onrender.com`
- **Repository**: Automatic deployment from GitHub

---

**Ready to start? Go to https://app.netlify.com/start and connect your GitHub repository!**
