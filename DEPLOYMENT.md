# Deployment Guide

Complete guide for deploying the Content Creation Engine to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Docker Deployment](#docker-deployment)
- [Reverse Proxy Setup](#reverse-proxy-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Linux server (Ubuntu 20.04+ recommended)
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage
- Root or sudo access
- Domain name (optional but recommended)

### Required Software

- Python 3.10+
- Node.js 18+
- nginx or Caddy (for reverse proxy)
- systemd (for process management)
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install nginx
sudo apt install nginx -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Create Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash cce
sudo passwd cce

# Add to www-data group
sudo usermod -a -G www-data cce
```

### 3. Setup Application Directory

```bash
# Switch to application user
sudo su - cce

# Clone or upload your application
cd /home/cce
# Upload your cce directory here
```

## Backend Deployment

### 1. Python Environment

```bash
cd /home/cce/cce/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### 2. Environment Configuration

```bash
# Create production .env file
cat > .env << EOF
# API Keys
ANTHROPIC_API_KEY=your_actual_api_key_here
FIRECRAWL_API_KEY=your_actual_firecrawl_key_here

# WordPress Configuration (optional)
WORDPRESS_SITE_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# Application Settings
APP_NAME=Content Creation Engine
DEBUG=false
MEMORY_BASE_PATH=/home/cce/cce/backend/app/memory

# Server Settings
HOST=127.0.0.1
PORT=8000
EOF

# Secure the .env file
chmod 600 .env
```

### 3. Create Systemd Service

```bash
# Create service file
sudo cat > /etc/systemd/system/cce-backend.service << EOF
[Unit]
Description=Content Creation Engine Backend
After=network.target

[Service]
Type=notify
User=cce
Group=www-data
WorkingDirectory=/home/cce/cce/backend
Environment="PATH=/home/cce/cce/backend/venv/bin"
ExecStart=/home/cce/cce/backend/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 300 \
    --access-logfile /var/log/cce/access.log \
    --error-logfile /var/log/cce/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/cce
sudo chown cce:www-data /var/log/cce

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cce-backend
sudo systemctl start cce-backend

# Check status
sudo systemctl status cce-backend
```

### 4. Test Backend

```bash
# Check if backend is responding
curl http://127.0.0.1:8000/health

# Should return: {"status":"healthy","service":"content-creation-engine"}
```

## Frontend Deployment

### 1. Build Frontend

```bash
cd /home/cce/cce/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Build output will be in /home/cce/cce/frontend/dist
```

### 2. Configure Frontend API Endpoint

If your backend is on a different domain, update the API base URL:

```bash
# Create production config
cat > /home/cce/cce/frontend/.env.production << EOF
VITE_API_BASE_URL=https://api.yourdomain.com
EOF

# Rebuild
npm run build
```

## Reverse Proxy Setup

### Option 1: Nginx (Recommended)

```bash
# Create nginx configuration
sudo cat > /etc/nginx/sites-available/cce << EOF
# Frontend server
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /home/cce/cce/frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend routes
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # SSE specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/cce /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Option 2: Caddy (Alternative)

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Create Caddyfile
sudo cat > /etc/caddy/Caddyfile << EOF
yourdomain.com {
    # Automatic HTTPS
    root * /home/cce/cce/frontend/dist
    file_server

    # API proxy
    handle /api/* {
        reverse_proxy localhost:8000 {
            flush_interval -1
        }
    }

    # SPA fallback
    try_files {path} /index.html

    # Security headers
    header {
        X-Frame-Options SAMEORIGIN
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
    }
}
EOF

# Reload Caddy
sudo systemctl reload caddy
```

## SSL Certificate Setup

### Using Let's Encrypt with Nginx

```bash
# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew
```

### Using Caddy

Caddy automatically obtains and renews SSL certificates. No additional configuration needed.

## Monitoring and Logging

### 1. Application Logs

```bash
# View backend logs
sudo journalctl -u cce-backend -f

# View nginx access logs
sudo tail -f /var/log/nginx/access.log

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# View application logs
sudo tail -f /var/log/cce/access.log
sudo tail -f /var/log/cce/error.log
```

### 2. Log Rotation

```bash
# Configure log rotation
sudo cat > /etc/logrotate.d/cce << EOF
/var/log/cce/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 cce www-data
    sharedscripts
    postrotate
        systemctl reload cce-backend
    endscript
}
EOF
```

### 3. System Monitoring

```bash
# Monitor system resources
htop

# Monitor disk usage
df -h

# Monitor memory usage
free -h

# Monitor backend process
ps aux | grep gunicorn
```

### 4. Application Health Checks

Create a monitoring script:

```bash
cat > /home/cce/check_health.sh << EOF
#!/bin/bash
response=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ \$response -eq 200 ]; then
    echo "Backend healthy"
else
    echo "Backend unhealthy - Response code: \$response"
    sudo systemctl restart cce-backend
fi
EOF

chmod +x /home/cce/check_health.sh

# Add to crontab for regular checks
crontab -e
# Add: */5 * * * * /home/cce/check_health.sh >> /var/log/cce/health-check.log 2>&1
```

## Security Considerations

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 2. Rate Limiting (Nginx)

```bash
# Add to nginx http block
sudo nano /etc/nginx/nginx.conf

# Add inside http block:
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Add to location /api/ block:
limit_req zone=api burst=20 nodelay;
```

### 3. API Key Security

```bash
# Ensure .env is not readable by others
chmod 600 /home/cce/cce/backend/.env

# Never commit .env to version control
echo ".env" >> /home/cce/cce/.gitignore
```

### 4. CORS Configuration

Update `/home/cce/cce/backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain only
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

### 5. Fail2Ban for SSH Protection

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Docker Deployment

### 1. Create Dockerfiles

Backend Dockerfile:
```dockerfile
# /home/cce/cce/backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY app app

# Create memory directory
RUN mkdir -p app/memory

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300"]
```

Frontend Dockerfile:
```dockerfile
# /home/cce/cce/frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Docker Compose

```yaml
# /home/cce/cce/docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: cce-backend
    restart: always
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app/memory:/app/app/memory
    networks:
      - cce-network

  frontend:
    build: ./frontend
    container_name: cce-frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - cce-network

networks:
  cce-network:
    driver: bridge
```

### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
sudo journalctl -u cce-backend -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Test Python application
cd /home/cce/cce/backend
source venv/bin/activate
python -c "from app.main import app; print('Import successful')"
```

### Frontend Build Fails

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Test nginx configuration
sudo nginx -t
```

### High Memory Usage

```bash
# Reduce Gunicorn workers in systemd service
# Edit: /etc/systemd/system/cce-backend.service
# Change --workers 4 to --workers 2

sudo systemctl daemon-reload
sudo systemctl restart cce-backend
```

### API Connection Timeouts

```bash
# Increase timeout in nginx config
# Add to location /api/ block:
proxy_read_timeout 600s;
proxy_connect_timeout 600s;
proxy_send_timeout 600s;

sudo nginx -t
sudo systemctl reload nginx
```

## Backup and Recovery

### Database Backup (if implemented)

```bash
# For now, sessions are in-memory
# Backup memory directory
tar -czf cce-memory-backup-$(date +%Y%m%d).tar.gz /home/cce/cce/backend/app/memory/
```

### Application Backup

```bash
# Backup entire application
cd /home/cce
tar -czf cce-backup-$(date +%Y%m%d).tar.gz cce/ --exclude=cce/backend/venv --exclude=cce/frontend/node_modules
```

### Automated Backups

```bash
# Create backup script
cat > /home/cce/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/cce/backups"
mkdir -p \$BACKUP_DIR
tar -czf \$BACKUP_DIR/cce-\$(date +%Y%m%d-%H%M%S).tar.gz /home/cce/cce --exclude=venv --exclude=node_modules
find \$BACKUP_DIR -name "cce-*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/cce/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/cce/backup.sh
```

## Updates and Maintenance

### Update Application

```bash
# Pull latest code
cd /home/cce/cce
git pull

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Rebuild frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart cce-backend
sudo systemctl reload nginx
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Reboot if required
sudo reboot
```

## Performance Optimization

### 1. Enable Caching

Add to nginx config:
```nginx
# Static file caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Increase Worker Processes

```bash
# Edit systemd service
# Change --workers 4 to --workers 8 (for 8+ core servers)
```

### 3. Enable HTTP/2

```nginx
listen 443 ssl http2;
```

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring script running
- [ ] Backups automated
- [ ] CORS properly configured
- [ ] Health checks working
- [ ] Error tracking configured
- [ ] API keys secured
- [ ] System updates automated

## Support

For deployment issues:
1. Check application logs
2. Verify all services are running
3. Test health endpoints
4. Review nginx/Caddy configuration
5. Check firewall rules
6. Verify DNS settings

---

**Production Deployment Complete!**

Your Content Creation Engine should now be running securely in production.
