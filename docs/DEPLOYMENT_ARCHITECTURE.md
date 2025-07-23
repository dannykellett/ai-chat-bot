# Deployment Architecture

**Version:** 1.0
**Date:** July 22, 2025

---

## Table of Contents
1. [Overview](#overview)
2. [Development Environment](#development-environment)
3. [Docker Architecture](#docker-architecture)
4. [Production Deployment Options](#production-deployment-options)
5. [Infrastructure as Code](#infrastructure-as-code)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Security Considerations](#security-considerations)
9. [Scaling Strategy](#scaling-strategy)
10. [Disaster Recovery](#disaster-recovery)

---

## Overview

This document outlines deployment strategies for the AI Chatbot application, from local development to production environments, with a focus on simplicity and educational value.

### Deployment Principles
- **Simplicity First**: Easy to deploy on a single VPS
- **Container-Based**: Docker for consistency across environments
- **Scalable Design**: Can grow from single server to distributed
- **Cost-Effective**: Works on budget hosting
- **Educational**: Clear documentation for learning

---

## Development Environment

### 2.1 Local Development Setup

```bash
# Project structure for development
ai-chatbot/
├── backend/
│   ├── .env.local
│   └── data/           # Local SQLite database
├── frontend-react/
│   └── .env.local
├── frontend-streamlit/
│   └── .env.local
├── docker/
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
└── scripts/
    ├── setup-dev.sh
    └── start-dev.sh
```

### 2.2 Development Scripts

```bash
#!/bin/bash
# scripts/setup-dev.sh

echo "🚀 Setting up AI Chatbot development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed."; exit 1; }

# Backend setup
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install uv
uv pip install -r requirements.txt
cp .env.example .env.local

# Frontend React setup
echo "⚛️ Setting up React frontend..."
cd ../frontend-react
npm install
cp .env.example .env.local

# Frontend Streamlit setup
echo "🎈 Setting up Streamlit frontend..."
cd ../frontend-streamlit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local

echo "✅ Development environment setup complete!"
echo "📝 Don't forget to add your OpenAI API key to the .env files"
```

### 2.3 Development Docker Compose

```yaml
# docker/docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.dev
    volumes:
      - ../backend:/app
      - backend-venv:/app/venv
    environment:
      - ENV=development
      - DATABASE_URL=sqlite+aiosqlite:///./data/dev.db
    env_file:
      - ../backend/.env.local
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend-react:
    build:
      context: ../frontend-react
      dockerfile: Dockerfile.dev
    volumes:
      - ../frontend-react:/app
      - react-node-modules:/app/node_modules
    env_file:
      - ../frontend-react/.env.local
    ports:
      - "3000:3000"
    command: npm run dev

  frontend-streamlit:
    build:
      context: ../frontend-streamlit
      dockerfile: Dockerfile.dev
    volumes:
      - ../frontend-streamlit:/app
      - streamlit-venv:/app/venv
    env_file:
      - ../frontend-streamlit/.env.local
    ports:
      - "8501:8501"
    command: streamlit run app.py --server.runOnSave=true

volumes:
  backend-venv:
  react-node-modules:
  streamlit-venv:
```

---

## Docker Architecture

### 3.1 Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 3.2 React Frontend Dockerfile

```dockerfile
# frontend-react/Dockerfile
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 3.3 Streamlit Frontend Dockerfile

```dockerfile
# frontend-streamlit/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3.4 Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx-cache:/var/cache/nginx
    depends_on:
      - backend
      - frontend-react
      - frontend-streamlit
    restart: unless-stopped
    networks:
      - chatbot-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - ENV=production
      - DATABASE_URL=sqlite+aiosqlite:///./data/prod.db
    env_file:
      - .env.prod
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - chatbot-network

  frontend-react:
    build:
      context: ./frontend-react
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=/api
    restart: unless-stopped
    networks:
      - chatbot-network

  frontend-streamlit:
    build:
      context: ./frontend-streamlit
      dockerfile: Dockerfile
    environment:
      - API_URL=http://backend:8000
    restart: unless-stopped
    networks:
      - chatbot-network

  # Optional: PostgreSQL for production
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=chatbot
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=chatbot
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - chatbot-network
    profiles:
      - postgres

networks:
  chatbot-network:
    driver: bridge

volumes:
  nginx-cache:
  postgres-data:
```

---

## Production Deployment Options

### 4.1 Single VPS Deployment

```bash
# Deploy to single VPS (Ubuntu 22.04)
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/chatbot
cd /opt/chatbot

# Clone repository
git clone https://github.com/yourusername/ai-chatbot.git .

# Create environment file
cp .env.example .env.prod
# Edit .env.prod with your settings

# Start application
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

### 4.2 Cloud Platform Deployments

#### AWS EC2 Deployment
```yaml
# terraform/aws/main.tf
provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "chatbot" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu 22.04
  instance_type = "t3.small"

  key_name = var.key_pair_name

  vpc_security_group_ids = [aws_security_group.chatbot.id]

  user_data = file("${path.module}/user-data.sh")

  tags = {
    Name = "ai-chatbot"
  }
}

resource "aws_security_group" "chatbot" {
  name        = "chatbot-sg"
  description = "Security group for AI Chatbot"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict in production
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

#### DigitalOcean Deployment
```yaml
# terraform/digitalocean/main.tf
provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "chatbot" {
  name     = "ai-chatbot"
  size     = "s-1vcpu-2gb"
  image    = "ubuntu-22-04-x64"
  region   = "nyc3"
  ssh_keys = [var.ssh_key_id]

  user_data = file("${path.module}/user-data.sh")
}

resource "digitalocean_firewall" "chatbot" {
  name = "chatbot-firewall"

  droplet_ids = [digitalocean_droplet.chatbot.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }
}
```

### 4.3 Hybrid Deployment

```yaml
# Hybrid deployment: Backend on VPS, Frontend on Vercel/Netlify

# Backend only docker-compose
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=https://yourchatbot.vercel.app
    env_file:
      - .env.prod
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    restart: unless-stopped

# Frontend deployment (vercel.json)
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://api.yourchatbot.com/api/$1"
    }
  ]
}
```

---

## Infrastructure as Code

### 5.1 Terraform Module Structure

```
terraform/
├── modules/
│   ├── vpc/
│   ├── compute/
│   ├── database/
│   └── monitoring/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── variables.tf
├── outputs.tf
└── main.tf
```

### 5.2 Complete Infrastructure

```hcl
# terraform/main.tf
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  environment = var.environment
}

module "compute" {
  source = "./modules/compute"

  vpc_id = module.vpc.vpc_id
  subnet_id = module.vpc.public_subnet_id
  instance_type = var.instance_type

  user_data = templatefile("${path.module}/user-data.sh", {
    docker_compose_file = file("${path.root}/../docker-compose.prod.yml")
    env_file = var.env_file_content
  })
}

module "database" {
  source = "./modules/database"
  count = var.use_rds ? 1 : 0

  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  engine = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"
}

module "monitoring" {
  source = "./modules/monitoring"

  instance_id = module.compute.instance_id
  sns_email = var.alert_email
}
```

---

## CI/CD Pipeline

### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements-test.txt
          pytest

      - name: Test React Frontend
        run: |
          cd frontend-react
          npm ci
          npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest

      - name: Build and push React Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend-react
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend-react:latest

      - name: Build and push Streamlit Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend-streamlit
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend-streamlit:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/chatbot
            git pull origin main
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
            docker system prune -f
```

### 6.2 Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting deployment..."

# Check if running on production server
if [ "$HOSTNAME" != "production-server" ]; then
  echo "❌ This script should only be run on the production server"
  exit 1
fi

# Backup database
echo "💾 Backing up database..."
docker-compose -f docker-compose.prod.yml exec -T backend \
  sqlite3 /app/data/prod.db ".backup '/app/data/backup-$(date +%Y%m%d-%H%M%S).db'"

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Update dependencies
echo "📦 Updating dependencies..."
docker-compose -f docker-compose.prod.yml build

# Run migrations
echo "🔄 Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend \
  alembic upgrade head

# Restart services
echo "🔄 Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

# Health check
echo "🏥 Running health checks..."
sleep 10
curl -f http://localhost/api/v1/health || exit 1

echo "✅ Deployment complete!"
```

---

## Monitoring and Logging

### 7.1 Logging Architecture

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./promtail/config.yml:/etc/promtail/config.yml:ro
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - chatbot-network

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki/config.yml:/etc/loki/config.yml:ro
      - loki-data:/loki
    command: -config.file=/etc/loki/config.yml
    networks:
      - chatbot-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - chatbot-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - chatbot-network

volumes:
  loki-data:
  prometheus-data:
  grafana-data:
```

### 7.2 Application Metrics

```python
# backend/app/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Request, Response
import time

# Define metrics
request_count = Counter(
    'chatbot_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'chatbot_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

active_sessions = Gauge(
    'chatbot_active_sessions',
    'Number of active sessions'
)

message_count = Counter(
    'chatbot_messages_total',
    'Total messages processed',
    ['role', 'model']
)

token_usage = Counter(
    'chatbot_tokens_total',
    'Total tokens used',
    ['model', 'type']
)

def setup_metrics(app: FastAPI):
    """Setup Prometheus metrics endpoint and middleware"""

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response

    @app.get("/metrics")
    async def metrics():
        return Response(
            generate_latest(),
            media_type="text/plain"
        )
```

### 7.3 Grafana Dashboard

```json
{
  "dashboard": {
    "title": "AI Chatbot Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(chatbot_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, chatbot_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "chatbot_active_sessions"
          }
        ]
      },
      {
        "title": "Token Usage",
        "targets": [
          {
            "expr": "rate(chatbot_tokens_total[1h])"
          }
        ]
      }
    ]
  }
}
```

---

## Security Considerations

### 8.1 Security Checklist

```yaml
# Security measures implemented

Application Security:
  - Input validation with Pydantic
  - SQL injection prevention via ORM
  - XSS protection in frontend
  - CSRF tokens for state-changing operations
  - Rate limiting per session
  - File upload restrictions

Infrastructure Security:
  - HTTPS enforcement
  - Firewall rules
  - Non-root Docker containers
  - Secret management
  - Regular security updates

Monitoring:
  - Failed authentication attempts
  - Unusual traffic patterns
  - Resource usage anomalies
  - Error rate monitoring
```

### 8.2 Secret Management

```bash
# Using Docker secrets in production
echo "your-secret-key" | docker secret create openai_api_key -
echo "your-db-password" | docker secret create db_password -

# docker-compose with secrets
version: '3.8'
services:
  backend:
    image: chatbot-backend
    secrets:
      - openai_api_key
      - db_password
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  openai_api_key:
    external: true
  db_password:
    external: true
```

---

## Scaling Strategy

### 9.1 Vertical Scaling

```bash
# Upgrade VPS resources
# DigitalOcean example
doctl compute droplet resize <droplet-id> --size s-2vcpu-4gb --wait

# AWS example
aws ec2 modify-instance-attribute \
  --instance-id <instance-id> \
  --instance-type t3.medium
```

### 9.2 Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    image: chatbot-backend
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  nginx:
    image: nginx
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    depends_on:
      - backend

configs:
  nginx_config:
    file: ./nginx/nginx-load-balanced.conf
```

### 9.3 Database Scaling

```yaml
# PostgreSQL with read replicas
version: '3.8'

services:
  postgres-primary:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPL_PASSWORD}

  postgres-replica:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_HOST=postgres-primary
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPL_PASSWORD}
    depends_on:
      - postgres-primary
```

---

## Disaster Recovery

### 10.1 Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=7
S3_BUCKET="chatbot-backups"

# Create backup directory
mkdir -p $BACKUP_DIR/$(date +%Y%m%d)

# Backup database
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U chatbot chatbot | \
  gzip > $BACKUP_DIR/$(date +%Y%m%d)/database.sql.gz

# Backup uploaded files
echo "Backing up files..."
tar -czf $BACKUP_DIR/$(date +%Y%m%d)/uploads.tar.gz ./uploads

# Backup configuration
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/$(date +%Y%m%d)/config.tar.gz \
  .env.prod \
  docker-compose.prod.yml \
  nginx/

# Upload to S3
echo "Uploading to S3..."
aws s3 sync $BACKUP_DIR/$(date +%Y%m%d) \
  s3://$S3_BUCKET/$(date +%Y%m%d)/

# Clean old backups
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;

echo "Backup complete!"
```

### 10.2 Recovery Procedures

```bash
#!/bin/bash
# scripts/restore.sh

# Configuration
BACKUP_DATE=$1
S3_BUCKET="chatbot-backups"

if [ -z "$BACKUP_DATE" ]; then
  echo "Usage: ./restore.sh YYYYMMDD"
  exit 1
fi

# Download from S3
echo "Downloading backup from S3..."
aws s3 sync s3://$S3_BUCKET/$BACKUP_DATE /tmp/restore/

# Stop services
echo "Stopping services..."
docker-compose -f docker-compose.prod.yml down

# Restore database
echo "Restoring database..."
gunzip < /tmp/restore/database.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U chatbot chatbot

# Restore files
echo "Restoring files..."
tar -xzf /tmp/restore/uploads.tar.gz -C ./

# Restore configuration
echo "Restoring configuration..."
tar -xzf /tmp/restore/config.tar.gz -C ./

# Restart services
echo "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "Restore complete!"
```

### 10.3 Disaster Recovery Plan

```markdown
# Disaster Recovery Runbook

## Incident Response

1. **Detection**
   - Monitor alerts from Grafana/Prometheus
   - Check service health endpoints
   - Verify user reports

2. **Assessment**
   - Determine scope of outage
   - Check infrastructure status
   - Review recent changes

3. **Communication**
   - Update status page
   - Notify stakeholders
   - Document incident timeline

## Recovery Procedures

### Scenario: Complete Server Failure

1. Provision new server
   ```bash
   terraform apply -var="environment=prod"
   ```

2. Restore from backup
   ```bash
   ./scripts/restore.sh $(date -d yesterday +%Y%m%d)
   ```

3. Update DNS
   ```bash
   doctl compute domain records update example.com \
     --record-id <id> --record-data <new-ip>
   ```

4. Verify services
   ```bash
   ./scripts/health-check.sh
   ```

### Scenario: Database Corruption

1. Stop application
   ```bash
   docker-compose -f docker-compose.prod.yml stop backend
   ```

2. Restore database from latest backup
   ```bash
   ./scripts/restore-db.sh
   ```

3. Verify data integrity
   ```sql
   SELECT COUNT(*) FROM conversations;
   SELECT COUNT(*) FROM messages;
   ```

4. Restart application
   ```bash
   docker-compose -f docker-compose.prod.yml start backend
   ```

## Post-Incident

1. **Root Cause Analysis**
   - Timeline of events
   - Contributing factors
   - Impact assessment

2. **Improvements**
   - Update runbooks
   - Improve monitoring
   - Implement preventive measures

3. **Testing**
   - Schedule disaster recovery drill
   - Update recovery procedures
   - Train team members
```

---

## Summary

This deployment architecture provides:

1. **Simple Start**: Easy single-server deployment
2. **Container-Based**: Consistent across environments
3. **Scalable Design**: Can grow from single VPS to distributed
4. **Comprehensive Monitoring**: Full observability stack
5. **Security First**: Built-in security measures
6. **Disaster Recovery**: Backup and restore procedures
7. **CI/CD Integration**: Automated deployment pipeline
8. **Cost-Effective**: Works on budget infrastructure

The design balances simplicity for learning with production-ready patterns that can scale with growth.
