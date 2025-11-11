# Deployment Guide

This guide provides detailed instructions for deploying the Secure File Sharing System to production.

## Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Railway Deployment](#railway-deployment)
3. [AWS EC2 Deployment](#aws-ec2-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Post-deployment Steps](#post-deployment-steps)

## Pre-deployment Checklist

### 1. Environment Configuration
- [ ] Set `DEBUG=False` in production
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure email settings for production SMTP
- [ ] Set up SSL/TLS certificates

### 2. Security Settings
```python
# Production settings
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

## Railway Deployment

Railway is a modern platform that makes deployment simple with automatic GitHub integration and PostgreSQL support.

### Step 1: Sign Up for Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Verify your account (credit card required for free tier)

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your file-sharing-system repository
4. Railway will automatically detect it's a Django project

### Step 3: Add PostgreSQL Database
1. In your project dashboard, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. The `DATABASE_URL` will be automatically set as an environment variable

### Step 4: Configure Environment Variables
In the Railway dashboard, go to your web service → Variables:

```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.up.railway.app
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

**Note:** `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

### Step 5: Configure Build & Deploy Settings

Railway automatically detects Django projects, but you can customize:

**Build Command** (optional):
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
python manage.py migrate && python manage.py create_ops_user --username opsuser --password opspass123 && gunicorn file_sharing_system.wsgi:application --bind 0.0.0.0:$PORT
```

### Step 6: Deploy
1. Railway will automatically deploy on every push to your main branch
2. Monitor the deployment logs in the Railway dashboard
3. Once deployed, Railway will provide a public URL

### Step 7: Create Operations User (if not done in start command)
```bash
# Using Railway CLI
railway run python manage.py create_ops_user

# Or via Railway dashboard shell
python manage.py create_ops_user --username opsuser --email ops@company.com
```

### Step 8: Custom Domain (Optional)
1. Go to Settings → Domains
2. Click "Add Domain"
3. Follow instructions to configure your DNS

### Railway CLI (Optional)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run commands
railway run python manage.py migrate
railway run python manage.py create_ops_user

# View logs
railway logs
```

### Advantages of Railway
- ✅ Automatic deployments from GitHub
- ✅ Built-in PostgreSQL with automatic DATABASE_URL
- ✅ Free tier with $5 monthly credit
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Built-in monitoring and logs
- ✅ No credit card required for trial

## AWS EC2 Deployment

### Step 1: Launch EC2 Instance
- Choose Ubuntu Server 22.04 LTS
- Instance type: t2.micro (free tier) or larger
- Configure security group:
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere

### Step 2: Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
```

### Step 4: Setup PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE file_sharing_db;
CREATE USER file_sharing_user WITH PASSWORD 'your-password';
ALTER ROLE file_sharing_user SET client_encoding TO 'utf8';
ALTER ROLE file_sharing_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE file_sharing_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE file_sharing_db TO file_sharing_user;
\q
```

### Step 5: Clone and Setup Project
```bash
cd /home/ubuntu
git clone your-repo-url
cd file_sharing_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Step 6: Configure Environment
```bash
nano .env
# Add production settings
```

### Step 7: Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic
python manage.py create_ops_user
```

### Step 8: Configure Gunicorn
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/file_sharing_system
ExecStart=/home/ubuntu/file_sharing_system/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ubuntu/file_sharing_system/file_sharing_system.sock \
          file_sharing_system.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Step 9: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/file_sharing_system
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/file_sharing_system;
    }
    
    location /media/ {
        root /home/ubuntu/file_sharing_system;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/file_sharing_system/file_sharing_system.sock;
    }
}
```

### Step 10: Enable and Start Services
```bash
sudo ln -s /etc/nginx/sites-available/file_sharing_system /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
```

## Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "file_sharing_system.wsgi:application"]
```

### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=file_sharing_db
      - POSTGRES_USER=file_sharing_user
      - POSTGRES_PASSWORD=your-password
    
  web:
    build: .
    command: gunicorn file_sharing_system.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Step 3: Build and Run
```bash
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_ops_user
```

## Post-deployment Steps

### 1. Setup SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. Setup Automated Backups
```bash
# Create backup script
nano /home/ubuntu/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U file_sharing_user file_sharing_db > /home/ubuntu/backups/db_$DATE.sql
find /home/ubuntu/backups -name "db_*.sql" -mtime +7 -delete
```

### 3. Setup Cron Job for Token Cleanup
```bash
crontab -e
# Add: 0 2 * * * cd /home/ubuntu/file_sharing_system && /home/ubuntu/file_sharing_system/venv/bin/python manage.py cleanup_expired_tokens
```

### 4. Monitor Application
- Setup logging with services like Sentry or Papertrail
- Configure monitoring with CloudWatch (AWS) or Heroku metrics
- Setup uptime monitoring with UptimeRobot or Pingdom

### 5. Performance Optimization
- Enable Redis for caching
- Configure CDN for static files (CloudFront, Cloudflare)
- Setup load balancing for high traffic

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# Check connection settings in .env
```

**Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn nginx
```

**Permission Denied on Media Files**
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/file_sharing_system/media
sudo chmod -R 755 /home/ubuntu/file_sharing_system/media
```

## Security Best Practices

1. **Never commit sensitive data** - Use environment variables
2. **Regular updates** - Keep dependencies updated
3. **Firewall configuration** - Only open necessary ports
4. **Database backups** - Automated daily backups
5. **SSL/TLS** - Always use HTTPS in production
6. **Rate limiting** - Implement API rate limiting
7. **Monitoring** - Setup alerts for suspicious activity

## Support

For deployment issues, contact: himanshusharma.dev80@gmail.com
