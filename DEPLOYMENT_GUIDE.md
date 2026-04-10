# Deployment Guide for Brain Tumor Segmentation System

## **Quick Deployment Options**

### **Option 1: Docker Deployment (Recommended)**
**Best for production and development**

#### **Step 1: Install Docker Desktop**
1. **Download**: https://www.docker.com/products/docker-desktop/
2. **Install**: Run the installer and restart your computer
3. **Verify**: Open PowerShell and run `docker --version`

#### **Step 2: Deploy with Docker Compose**
```bash
# Navigate to project directory
cd "c:\Users\MASUKA  CHRISTIAN\CascadeProjects\brain-tumor-segmentation"

# Build and start all services
docker-compose up -d

# Check deployment status
docker-compose ps

# View logs
docker-compose logs -f
```

#### **Step 3: Access Your Application**
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379

#### **Step 4: Stop Services**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean start)
docker-compose down -v
```

---

### **Option 2: Local Development Deployment**
**Best for testing and development**

#### **Step 1: Backend Deployment**
```bash
# Navigate to project directory
cd "c:\Users\MASUKA  CHRISTIAN\CascadeProjects\brain-tumor-segmentation"

# Activate virtual environment
medseg_env\Scripts\activate

# Navigate to backend
cd objective3_interface/backend

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Step 2: Frontend Deployment**
```bash
# Open new terminal
cd "c:\Users\MASUKA  CHRISTIAN\CascadeProjects\brain-tumor-segmentation"

# Navigate to frontend
cd objective3_interface/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### **Step 3: Access Application**
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

### **Option 3: Production Server Deployment**
**Best for production hosting**

#### **Step 1: Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **Step 2: Deploy Application**
```bash
# Clone repository
git clone https://github.com/mudimut89/Medical-Image-Segmentation-for-Brain-Tumor-Prognosis.git
cd Medical-Image-Segmentation-for-Brain-Tumor-Prognosis

# Deploy with Docker Compose
docker-compose up -d

# Setup SSL (optional)
sudo apt install certbot
sudo certbot --nginx -d yourdomain.com
```

---

## **Environment Configuration**

### **Development Environment (.env)**
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/brain_tumor
REDIS_URL=redis://localhost:6379/0

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Model Paths
MODEL_PATH=./models/weights/
UPLOAD_PATH=./uploads/
LOG_PATH=./logs/
```

### **Production Environment (.env.prod)**
```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/brain_tumor_prod
REDIS_URL=redis://redis:6379/0

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# SSL
SSL_CERT_PATH=/etc/ssl/certs/yourdomain.crt
SSL_KEY_PATH=/etc/ssl/private/yourdomain.key
```

---

## **Database Setup**

### **PostgreSQL Configuration**
```sql
-- Create database
CREATE DATABASE brain_tumor;

-- Create user
CREATE USER brain_tumor_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE brain_tumor TO brain_tumor_user;

-- Create tables (automatically done by Django/SQLAlchemy)
```

### **Database Migration**
```bash
# Using Alembic (if configured)
cd objective3_interface/backend
alembic upgrade head

# Manual table creation
psql -h localhost -U postgres -d brain_tumor -f scripts/init.sql
```

---

## **Monitoring and Logging**

### **Application Logs**
```bash
# View Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View specific service logs
docker-compose logs -f db
docker-compose logs -f redis
```

### **Health Checks**
```bash
# Check service health
curl http://localhost:8000/health

# Check database connection
docker-compose exec db pg_isready

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### **Performance Monitoring**
```bash
# View resource usage
docker stats

# View container status
docker-compose ps

# View system resources
htop
```

---

## **Security Configuration**

### **SSL/TLS Setup**
```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/certificate.crt

# Use Let's Encrypt (production)
sudo certbot --nginx -d yourdomain.com
```

### **Firewall Configuration**
```bash
# Configure UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### **Environment Variables Security**
```bash
# Set secure permissions
chmod 600 .env.prod

# Use Docker secrets (production)
echo "your-secret-key" | docker secret create db_password -
```

---

## **Backup and Recovery**

### **Database Backup**
```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U postgres brain_tumor > backup.sql

# Automated backup
crontab -e
# Add: 0 2 * * * docker-compose exec db pg_dump -U postgres brain_tumor > /backups/backup_$(date +\%Y\%m\%d).sql
```

### **Data Recovery**
```bash
# Restore database
docker-compose exec -T db psql -U postgres brain_tumor < backup.sql

# Restore from volume
docker-compose down
docker volume restore brain_tumor_postgres_data
docker-compose up -d
```

---

## **Scaling and Load Balancing**

### **Horizontal Scaling**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf
```

### **Load Balancer Configuration**
```nginx
# nginx/load-balancer.conf
upstream backend {
    server backend:8000;
    server backend:8000;
    server backend:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## **Troubleshooting**

### **Common Issues**

#### **Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 <PID>
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose exec db pg_isready

# Test connection
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:password@db:5432/brain_tumor'); print(engine.execute('SELECT 1').scalar())"
```

#### **Build Issues**
```bash
# Rebuild containers
docker-compose build --no-cache

# Clear Docker cache
docker system prune -a
```

### **Performance Issues**
```bash
# Check resource usage
docker stats

# Optimize database
docker-compose exec db psql -U postgres -d brain_tumor -c "VACUUM ANALYZE;"

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## **Deployment Checklist**

### **Pre-Deployment**
- [ ] Docker Desktop installed
- [ ] Environment variables configured
- [ ] SSL certificates obtained (production)
- [ ] Database credentials secured
- [ ] Firewall rules configured

### **Deployment**
- [ ] Code pushed to GitHub
- [ ] Docker images built successfully
- [ ] Services started without errors
- [ ] Health checks passing
- [ ] Load balancer configured

### **Post-Deployment**
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Backup schedule set
- [ ] SSL certificates renewed
- [ ] Performance optimized

---

## **Quick Start Commands**

### **Development**
```bash
# Quick dev setup
docker-compose -f docker-compose.dev.yml up -d
```

### **Production**
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### **Testing**
```bash
# Run tests
docker-compose exec backend pytest
```

### **Monitoring**
```bash
# View logs
docker-compose logs -f
```

---

## **Support**

### **Get Help**
- **Documentation**: Check inline comments and README files
- **Issues**: Create GitHub issue for bugs
- **Community**: Join Discord/Slack for support
- **Email**: Contact maintainer for enterprise support

### **Emergency Procedures**
1. **Check logs**: `docker-compose logs`
2. **Restart services**: `docker-compose restart`
3. **Restore backup**: Use backup procedures above
4. **Contact support**: Create urgent GitHub issue

---

**Your brain tumor segmentation system is ready for deployment! Choose the option that best fits your needs.**
