# Non-Docker Deployment Options for Brain Tumor Segmentation System

## **Option 1: Direct Python/Node.js Deployment**
**Best for simple development and testing**

### **Backend Deployment (Python/FastAPI)**

#### **Step 1: Setup Python Environment**
```bash
# Create virtual environment
python -m venv brain_tumor_env

# Activate environment
# Windows:
brain_tumor_env\Scripts\activate
# Linux/Mac:
source brain_tumor_env/bin/activate

# Install dependencies
pip install fastapi uvicorn tensorflow opencv-python numpy pillow python-multipart
```

#### **Step 2: Start Backend Server**
```bash
# Navigate to backend directory
cd objective3_interface/backend

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **Frontend Deployment (Node.js/React)**

#### **Step 1: Setup Node.js Environment**
```bash
# Check Node.js version (should be 18+)
node --version
npm --version

# If not installed, download from: https://nodejs.org/
```

#### **Step 2: Start Frontend Server**
```bash
# Navigate to frontend directory
cd objective3_interface/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### **Step 3: Build for Production**
```bash
# Build static files
npm run build

# Serve with any web server
npm install -g serve
serve -s dist -l 80
```

---

## **Option 2: IIS Deployment (Windows)**
**Best for Windows Server environments**

### **Step 1: Install IIS**
```powershell
# Enable IIS features
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpErrors
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpLogging
Enable-WindowsOptionalFeature -Online -FeatureName IIS-StaticContent
```

### **Step 2: Deploy Frontend to IIS**
```bash
# Build frontend
cd objective3_interface/frontend
npm run build

# Copy dist folder to IIS wwwroot
xcopy dist "C:\inetpub\wwwroot\brain-tumor\" /E /I
```

### **Step 3: Setup Backend as Windows Service**
```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

# Install backend as service
nssm install "BrainTumorBackend" "C:\path\to\brain_tumor_env\Scripts\python.exe"
nssm set "BrainTumorBackend" Arguments "C:\path\to\objective3_interface\backend\main.py"
nssm set "BrainTumorBackend" AppDirectory "C:\path\to\objective3_interface\backend"
nssm start "BrainTumorBackend"
```

---

## **Option 3: Apache Deployment (Linux)**
**Best for Linux servers**

### **Step 1: Install Apache**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install apache2

# CentOS/RHEL
sudo yum install httpd
sudo systemctl start httpd
sudo systemctl enable httpd
```

### **Step 2: Deploy Frontend**
```bash
# Build frontend
cd objective3_interface/frontend
npm run build

# Copy to Apache webroot
sudo cp -r dist/* /var/www/html/
```

### **Step 3: Setup Backend with mod_wsgi**
```bash
# Install mod_wsgi
sudo apt install libapache2-mod-wsgi-py3

# Create WSGI configuration
sudo nano /etc/apache2/sites-available/brain-tumor.conf
```

### **Apache Configuration**
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /var/www/html

    # Backend API
    WSGIScriptAlias /api /path/to/backend/app.wsgi
    <Directory /path/to/backend>
        Require all granted
    </Directory>

    # Frontend static files
    Alias /static /var/www/html/static
    <Directory /var/www/html>
        Require all granted
    </Directory>
</VirtualHost>
```

---

## **Option 4: Nginx + Gunicorn (Linux)**
**Best for high-performance Linux deployment**

### **Step 1: Install Nginx and Gunicorn**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx python3-pip

# Install Gunicorn
pip3 install gunicorn
```

### **Step 2: Setup Backend with Gunicorn**
```bash
# Create Gunicorn service file
sudo nano /etc/systemd/system/brain-tumor-backend.service
```

### **Systemd Service Configuration**
```ini
[Unit]
Description=Brain Tumor Segmentation Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/objective3_interface/backend
Environment="PATH=/path/to/brain_tumor_env/bin"
ExecStart=/path/to/brain_tumor_env/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Step 3: Configure Nginx**
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/brain-tumor
```

### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend static files
    location / {
        root /path/to/objective3_interface/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets
    location /static/ {
        root /path/to/objective3_interface/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### **Step 4: Start Services**
```bash
# Enable and start services
sudo systemctl enable brain-tumor-backend
sudo systemctl start brain-tumor-backend

sudo systemctl enable nginx
sudo systemctl start nginx

sudo ln -s /etc/nginx/sites-available/brain-tumor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## **Option 5: Cloud Platform Deployment**
**Best for scalable cloud hosting**

### **AWS EC2 Deployment**
```bash
# Launch EC2 instance (Ubuntu 20.04)
# Security Group: Allow ports 80, 443, 22

# SSH into instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

# Clone repository
git clone https://github.com/mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis.git
cd Medical-Image-Segmentation-for-Brain-Tumor-Prognosis

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r objective3_interface/backend/requirements.txt

# Setup frontend
cd objective3_interface/frontend
npm install
npm run build

# Configure Nginx (similar to Option 4)
sudo cp -r dist/* /var/www/html/
```

### **Heroku Deployment**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Create requirements.txt for backend
pip freeze > requirements.txt

# Deploy
heroku create your-app-name
git push heroku main
heroku open
```

### **Vercel Deployment (Frontend Only)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd objective3_interface/frontend
vercel --prod

# Backend can be deployed separately on Railway, Render, or similar
```

---

## **Option 6: Traditional Web Server (XAMPP/WAMP)**
**Best for Windows development**

### **XAMPP Deployment**
```bash
# Download and install XAMPP from: https://www.apachefriends.org/

# Start Apache and MySQL from XAMPP Control Panel

# Deploy frontend
cd objective3_interface/frontend
npm run build

# Copy to htdocs
xcopy dist "C:\xampp\htdocs\brain-tumor\" /E /I

# Access at: http://localhost/brain-tumor/
```

### **Backend as Separate Service**
```bash
# Run backend in separate terminal
cd objective3_interface/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend will call backend API at http://localhost:8000
```

---

## **Option 7: Python Web Server (Simple)**
**Best for quick testing**

### **Step 1: Build Frontend**
```bash
cd objective3_interface/frontend
npm run build
```

### **Step 2: Serve with Python**
```bash
# Serve static files
cd dist
python -m http.server 8080

# Or serve with Node.js
npx serve -s . -l 8080
```

### **Step 3: Run Backend Separately**
```bash
# In separate terminal
cd objective3_interface/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## **Database Setup (Non-Docker)**

### **PostgreSQL Local Installation**
```bash
# Windows: Download from https://www.postgresql.org/download/windows/
# Linux: sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb brain_tumor

# Create user
sudo -u postgres createuser brain_tumor_user

# Set password
sudo -u postgres psql
ALTER USER brain_tumor_user PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE brain_tumor TO brain_tumor_user;
\q
```

### **SQLite (Simpler Option)**
```python
# Modify backend to use SQLite
# In objective3_interface/backend/main.py or database config:

DATABASE_URL = "sqlite:///./brain_tumor.db"
```

### **MySQL Alternative**
```bash
# Install MySQL
sudo apt install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE brain_tumor;
CREATE USER 'brain_tumor_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON brain_tumor.* TO 'brain_tumor_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## **Environment Configuration**

### **Development (.env)**
```env
# Database
DATABASE_URL=sqlite:///./brain_tumor.db
# Or: postgresql://brain_tumor_user:password@localhost/brain_tumor

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key

# Paths
UPLOAD_PATH=./uploads/
MODEL_PATH=./models/
LOG_PATH=./logs/
```

### **Production (.env.prod)**
```env
# Database
DATABASE_URL=postgresql://brain_tumor_user:password@localhost/brain_tumor

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-very-secure-secret-key

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ORIGINS=http://localhost,http://yourdomain.com
```

---

## **Quick Start Scripts**

### **Windows Development (deploy-dev-windows.bat)**
```batch
@echo off
echo Starting Brain Tumor Segmentation (Windows Development)

REM Start Backend
start "Backend" cmd /k "cd objective3_interface\backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Start Frontend
start "Frontend" cmd /k "cd objective3_interface\frontend && npm run dev"

echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
```

### **Linux Development (deploy-dev-linux.sh)**
```bash
#!/bin/bash
echo "Starting Brain Tumor Segmentation (Linux Development)"

# Start Backend
cd objective3_interface/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Start Frontend
cd ../frontend
npm run dev &

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
wait
```

---

## **Recommendations**

### **For Development**
- **Option 1**: Direct Python/Node.js (easiest)
- **Option 6**: Python web server (quickest)

### **For Production**
- **Option 4**: Nginx + Gunicorn (best performance)
- **Option 2**: IIS (Windows Server)
- **Option 5**: Cloud platforms (scalable)

### **For Testing**
- **Option 7**: Simple HTTP server (minimal setup)
- **Option 1**: Direct deployment (full control)

---

## **Troubleshooting**

### **Common Issues**
- **Port conflicts**: Change ports in configuration
- **Permissions**: Use sudo/administrator rights
- **Dependencies**: Install missing packages
- **Firewall**: Allow required ports (80, 443, 8000)

### **Performance Tips**
- Use production web server (Gunicorn/uWSGI)
- Enable compression in Nginx/Apache
- Use CDN for static files
- Optimize database queries

---

**Choose the deployment option that best fits your environment and requirements!**
