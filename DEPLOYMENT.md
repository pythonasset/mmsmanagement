# Deployment Guide - Maintenance Management System

## Local Development Deployment

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 2GB RAM minimum
- Modern web browser

### Steps
```bash
# Navigate to project
cd maintenance_management_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

Access at: http://localhost:8501

---

## Streamlit Cloud Deployment (Free)

### Prerequisites
- GitHub account
- Streamlit Cloud account (https://streamlit.io/cloud)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Select your repository
- Set main file path: `app.py`
- Click "Deploy"

3. **Configure Secrets** (if needed)
- Go to App Settings → Secrets
- Add any API keys or credentials

### Advantages
- Free hosting
- Automatic updates from GitHub
- HTTPS included
- Easy sharing

---

## Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  maintenance-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=sqlite:///data/maintenance_management.db
    restart: unless-stopped
```

### Deploy
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## AWS Deployment

### Option 1: AWS EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t2.small or larger
   - Configure security group: Allow port 8501

2. **Connect and Install**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone <your-repo-url>
cd maintenance_management_system

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with screen/tmux
screen -S maintenance
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Detach: Ctrl+A, D
```

3. **Setup as Service**
Create `/etc/systemd/system/maintenance.service`:
```ini
[Unit]
Description=Maintenance Management System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/maintenance_management_system
Environment="PATH=/home/ubuntu/maintenance_management_system/venv/bin"
ExecStart=/home/ubuntu/maintenance_management_system/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable maintenance
sudo systemctl start maintenance
```

### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize and Deploy**
```bash
eb init -p python-3.9 maintenance-app --region us-east-1
eb create maintenance-env
eb open
```

---

## Azure Deployment

### Azure App Service

1. **Create App Service**
```bash
# Install Azure CLI
az login

# Create resource group
az group create --name maintenance-rg --location eastus

# Create app service plan
az appservice plan create --name maintenance-plan --resource-group maintenance-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group maintenance-rg --plan maintenance-plan --name maintenance-app --runtime "PYTHON:3.9"
```

2. **Deploy Code**
```bash
# Deploy from local Git
az webapp deployment source config-local-git --name maintenance-app --resource-group maintenance-rg

# Push code
git remote add azure <git-url>
git push azure main
```

---

## Google Cloud Deployment

### Google Cloud Run

1. **Create Dockerfile** (see Docker section)

2. **Deploy to Cloud Run**
```bash
# Install gcloud CLI
gcloud init

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/<project-id>/maintenance-app

# Deploy to Cloud Run
gcloud run deploy maintenance-app \
  --image gcr.io/<project-id>/maintenance-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## On-Premise Server Deployment

### Ubuntu Server Setup

1. **Install Prerequisites**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y
```

2. **Setup Application**
```bash
# Create app directory
sudo mkdir -p /var/www/maintenance
sudo chown $USER:$USER /var/www/maintenance

# Copy files
cp -r maintenance_management_system/* /var/www/maintenance/

# Setup virtual environment
cd /var/www/maintenance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/maintenance`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/maintenance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Database Migration (SQLite to PostgreSQL)

### Install PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
```

### Create Database
```bash
sudo -u postgres psql
CREATE DATABASE maintenance_db;
CREATE USER maintenance_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE maintenance_db TO maintenance_user;
\q
```

### Update Configuration
Edit `config/settings.py`:
```python
DATABASE_PATH = 'postgresql://maintenance_user:your-password@localhost/maintenance_db'
```

### Install PostgreSQL Driver
```bash
pip install psycopg2-binary
```

---

## Production Checklist

### Security
- [ ] Change default database password
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up user authentication
- [ ] Enable audit logging
- [ ] Regular security updates

### Performance
- [ ] Migrate to PostgreSQL for production
- [ ] Configure database connection pooling
- [ ] Enable caching
- [ ] Set up CDN for static assets
- [ ] Monitor application performance

### Backup
- [ ] Configure automated database backups
- [ ] Set up backup retention policy
- [ ] Test restore procedures
- [ ] Document backup locations

### Monitoring
- [ ] Set up application monitoring
- [ ] Configure error alerting
- [ ] Enable access logging
- [ ] Monitor disk usage
- [ ] Track application metrics

### Documentation
- [ ] Document deployment procedure
- [ ] Create runbooks for common issues
- [ ] Document backup/restore process
- [ ] Maintain change log

---

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use shared database (PostgreSQL)
- Implement session management
- Configure health checks

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Add database indexes
- Enable query caching

---

## Troubleshooting

### Application Won't Start
```bash
# Check Python version
python --version

# Verify dependencies
pip list

# Check for port conflicts
sudo netstat -tulpn | grep 8501
```

### Database Connection Issues
```bash
# Check database file permissions
ls -l data/maintenance_management.db

# Verify database integrity
sqlite3 data/maintenance_management.db "PRAGMA integrity_check;"
```

### Performance Issues
```bash
# Monitor system resources
htop

# Check application logs
streamlit run app.py --logger.level=debug

# Analyze database queries
# Enable SQL logging in database.py
```

---

## Maintenance

### Regular Tasks
- **Daily:** Monitor error logs
- **Weekly:** Review application performance
- **Monthly:** Update dependencies
- **Quarterly:** Security audit

### Backup Schedule
```bash
# Add to crontab
# Daily backup at 2 AM
0 2 * * * cp /var/www/maintenance/data/maintenance_management.db /backups/daily/maintenance_$(date +\%Y\%m\%d).db

# Weekly backup at 3 AM Sunday
0 3 * * 0 cp /var/www/maintenance/data/maintenance_management.db /backups/weekly/maintenance_$(date +\%Y\%m\%d).db
```

---

## Support

For deployment issues:
- Check application logs
- Review system logs
- Verify network connectivity
- Contact support: support@example.com

---

**Last Updated:** October 2025
