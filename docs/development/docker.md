# Docker Deployment Guide

Deploy Project Thalassa using Docker for consistent, scalable deployment across environments.

## Quick Start

### Build and Run

```bash
# Build the Docker image
docker build -t thalassa:latest .

# Run the container
docker run -d \
  --name thalassa \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  --env-file .env.production \
  thalassa:latest
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Dockerfile

The multi-stage Dockerfile optimizes for size and security:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 thalassa && \
    mkdir -p /app/uploads /app/results /app/logs && \
    chown -R thalassa:thalassa /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY --chown=thalassa:thalassa . .

# Switch to non-root user
USER thalassa

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: thalassa-app
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results
      - ./logs:/app/logs
    environment:
      - APP_NAME=Project Thalassa
      - APP_VERSION=1.0.0
      - DEBUG=false
      - ENVIRONMENT=production
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - thalassa-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: thalassa-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./static:/usr/share/nginx/html/static:ro
    depends_on:
      - app
    networks:
      - thalassa-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: thalassa-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - thalassa-network
    restart: unless-stopped
    command: redis-server --appendonly yes

networks:
  thalassa-network:
    driver: bridge

volumes:
  redis-data:
    driver: local
```

## Environment Configuration

### Development

`.env.development`:
```ini
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key
BEARER_TOKEN=dev-bearer-token
```

### Production

`.env.production`:
```ini
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
SECRET_KEY=<generate-secure-key>
BEARER_TOKEN=<generate-secure-token>
ALLOWED_ORIGINS=https://yourdomain.com
```

## Nginx Configuration

Create `nginx.conf` for reverse proxy:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        client_max_body_size 100M;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /static {
            alias /usr/share/nginx/html/static;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## Deployment Commands

### Building Images

```bash
# Build with tag
docker build -t thalassa:v1.0.0 .

# Build with build args
docker build \
  --build-arg VERSION=1.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t thalassa:latest .

# Multi-platform build
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t thalassa:latest \
  --push .
```

### Running Containers

```bash
# Run with resource limits
docker run -d \
  --name thalassa \
  --memory="1g" \
  --cpus="2" \
  -p 8000:8000 \
  thalassa:latest

# Run with custom network
docker network create thalassa-net
docker run -d \
  --name thalassa \
  --network thalassa-net \
  -p 8000:8000 \
  thalassa:latest

# Run with restart policy
docker run -d \
  --name thalassa \
  --restart=unless-stopped \
  -p 8000:8000 \
  thalassa:latest
```

### Container Management

```bash
# View logs
docker logs -f thalassa

# Execute commands in container
docker exec -it thalassa bash

# Copy files to/from container
docker cp local-file.txt thalassa:/app/
docker cp thalassa:/app/results.json ./

# Inspect container
docker inspect thalassa

# View resource usage
docker stats thalassa
```

## Volume Management

### Persistent Data

```bash
# Create named volumes
docker volume create thalassa-uploads
docker volume create thalassa-results

# Run with named volumes
docker run -d \
  -v thalassa-uploads:/app/uploads \
  -v thalassa-results:/app/results \
  thalassa:latest

# Backup volumes
docker run --rm \
  -v thalassa-uploads:/source \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/uploads.tar.gz -C /source .

# Restore volumes
docker run --rm \
  -v thalassa-uploads:/target \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/uploads.tar.gz -C /target
```

## Health Monitoring

### Health Check Implementation

```python
# app/health.py
from fastapi import APIRouter
from datetime import datetime
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": check_database(),
            "storage": check_storage(),
            "memory": check_memory(),
        }
    }

def check_memory():
    """Check memory usage."""
    memory = psutil.virtual_memory()
    return {
        "used_percent": memory.percent,
        "available_mb": memory.available / 1024 / 1024
    }
```

### Monitoring with Prometheus

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
```

## Security Best Practices

### Image Security

```dockerfile
# Use specific version tags
FROM python:3.11.5-slim

# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser app/ /app/

# Use secrets at build time
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) \
    python setup.py

# Scan for vulnerabilities
# docker scan thalassa:latest
```

### Runtime Security

```bash
# Run with security options
docker run -d \
  --name thalassa \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --read-only \
  --tmpfs /tmp \
  thalassa:latest

# Use secrets management
docker secret create api_key api_key.txt
docker service create \
  --name thalassa \
  --secret api_key \
  thalassa:latest
```

## Orchestration

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml thalassa

# Scale service
docker service scale thalassa_app=3

# Update service
docker service update \
  --image thalassa:v1.0.1 \
  thalassa_app
```

### Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thalassa
spec:
  replicas: 3
  selector:
    matchLabels:
      app: thalassa
  template:
    metadata:
      labels:
        app: thalassa
    spec:
      containers:
      - name: app
        image: thalassa:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: thalassa-uploads
```

## Troubleshooting

### File Permission Issues (Most Common)

**Symptoms:**
- `[Errno 13] Permission denied: 'uploads/filename.fastq'` when uploading files
- Cannot write to `/app/uploads`, `/app/results`, or `/app/logs`
- File operations fail in container

**Root Cause:**
Docker containers run with different user IDs than your host system, causing permission mismatches with mounted volumes.

**Solutions:**

1. **For Production (Named Volumes - Recommended):**
   ```bash
   # Use docker-compose.yml - handles permissions automatically with named volumes
   docker-compose up -d
   ```

2. **For Development (Bind Mounts):**
   ```bash
   # Ensure your host user has UID 1000
   id  # Should show uid=1000

   # Use development docker-compose
   docker-compose -f docker-compose.dev.yml up --build

   # Or specify user explicitly:
   docker run -d --user "$(id -u):$(id -g)" -p 8000:8000 \
     -v $(pwd)/uploads:/app/uploads thalassa:latest
   ```

3. **Fix Existing Directory Permissions:**
   ```bash
   # On host system, ensure correct ownership:
   sudo chown -R $(id -u):$(id -g) uploads/ results/ logs/
   chmod 755 uploads/ results/ logs/
   ```

4. **Platform-Specific Solutions:**

   **Linux (Primary Platform):**
   - Default configuration works (UID 1000)
   - Dockerfile creates user with UID 1000

   **macOS:**
   ```bash
   # Check your UID (may be different)
   id
   # Update user in docker-compose.dev.yml if needed:
   # user: "501:20"  # Common macOS values
   ```

   **Windows (WSL2):**
   ```bash
   # Ensure WSL2 permissions match
   sudo chown -R $(whoami):$(whoami) uploads/ results/ logs/
   ```

## Running Commands in Pixi Containers

### Understanding the Pixi Environment

This project uses [Pixi](https://pixi.sh) for environment management in Docker containers. The Dockerfile follows best practices by:
- Using multi-stage builds with the official Pixi base image
- Creating a shell-hook activation script (`pixi shell-hook`)
- Using an entrypoint that activates the Pixi environment before running commands
- Not including the Pixi executable in the final production image (for security and size)

### Executing Scripts in Containers

#### Method 1: Using the Entrypoint (Recommended for Production)
```bash
# Run Python scripts through the entrypoint that activates Pixi
docker compose exec app /app/entrypoint.sh python scripts/generate_results.py

# Run any command with Pixi environment activated
docker compose exec app /app/entrypoint.sh python --version
docker compose exec app /app/entrypoint.sh pytest
```

#### Method 2: Using Direct Binary Paths (Advanced)
```bash
# Use full path to Python in Pixi environment
docker compose exec app /app/.pixi/envs/prod/bin/python scripts/generate_results.py
```

### Pixi Tasks Integration

The project includes predefined Pixi tasks in `pixi.toml`:
```bash
# Available tasks (when Pixi executable is present):
pixi run analyze                # Generate analysis results
pixi run generate-results       # Same as analyze
pixi run batch-analysis         # Same as analyze
pixi run test                   # Run tests
pixi run lint                   # Code linting
```

**In Docker containers:**
```bash
# Since Pixi executable is not in production image, use entrypoint:
docker compose exec app /app/entrypoint.sh python scripts/generate_results.py
```

### Development vs Production

**Local Development (with Pixi installed):**
```bash
pixi run analyze               # Direct task execution
pixi shell                     # Enter Pixi shell
```

**Production Containers:**
```bash
# Method 1: Execute in running container
docker compose exec app /app/entrypoint.sh python scripts/generate_results.py
docker compose exec app /app/entrypoint.sh pytest

# Method 2: Use dedicated script runner service
docker-compose --profile scripts run --rm scripts
```

### Common Issues

#### Container won't start
```bash
# Check logs
docker logs thalassa

# Check events
docker events --filter container=thalassa

# Debug mode
docker run -it --entrypoint /bin/bash thalassa:latest
```

#### Legacy Permission Issues (If Above Doesn't Work)
```bash
# Fix volume permissions inside container
docker exec thalassa chown -R thalassa:thalassa /app/uploads

# Run with user namespace remapping
docker run --userns-remap=default thalassa:latest

# Check container user info
docker exec thalassa id
```

#### Network issues
```bash
# Test connectivity
docker exec thalassa ping -c 3 google.com

# Check network
docker network inspect bridge

# Test internal DNS
docker exec thalassa nslookup app
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        push: true
        tags: |
          user/thalassa:latest
          user/thalassa:${{ github.ref_name }}
```

## Performance Optimization

### Image Optimization

```dockerfile
# Use slim base images
FROM python:3.11-slim

# Minimize layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y

# Use .dockerignore
# .dockerignore
__pycache__
*.pyc
.git
.env
tests/
docs/
```

### Runtime Optimization

```bash
# Enable BuildKit
DOCKER_BUILDKIT=1 docker build .

# Use cache mounting
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Multi-stage parallel builds
docker buildx build \
  --target backend \
  --target frontend \
  --parallel .
```
