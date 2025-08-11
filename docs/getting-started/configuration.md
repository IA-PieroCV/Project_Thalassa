# Configuration Guide

This guide covers all configuration options for Project Thalassa.

## Environment Variables

Project Thalassa uses environment variables for configuration. Copy `.env.example` to `.env` and customize as needed.

### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | "Project Thalassa" | Application display name |
| `APP_VERSION` | string | "1.0.0" | Current application version |
| `DEBUG` | boolean | true | Enable debug mode (set to false in production) |
| `ENVIRONMENT` | string | "development" | Environment name (development/staging/production) |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | "0.0.0.0" | Server bind address |
| `PORT` | integer | 8000 | Server port number |

### Security Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | string | - | **REQUIRED**: Secret key for JWT tokens and security |
| `BEARER_TOKEN` | string | - | **REQUIRED**: Bearer token for API authentication |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | 30 | Token expiration time in minutes |

⚠️ **Security Warning**: Always generate new secure tokens for production:

```bash
# Generate a secure secret key
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"

# Generate a secure bearer token
python3 -c "import secrets; print('BEARER_TOKEN:', secrets.token_hex(64))"
```

### File Storage

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `UPLOAD_DIR` | string | "uploads" | Directory for uploaded files |
| `RESULTS_DIR` | string | "results" | Directory for analysis results |
| `MAX_FILE_SIZE_MB` | integer | 100 | Maximum upload file size in MB |

### Logging

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | "INFO" | Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `LOG_FILE` | string | "logs/thalassa.log" | Log file path |

### CORS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ALLOWED_ORIGINS` | string | "http://localhost:3000,http://localhost:8080" | Comma-separated list of allowed CORS origins |

### Risk Assessment Thresholds

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CRITICAL_RISK_THRESHOLD` | float | 0.8 | Threshold for critical risk classification |
| `HIGH_RISK_THRESHOLD` | float | 0.6 | Threshold for high risk classification |
| `MEDIUM_RISK_THRESHOLD` | float | 0.4 | Threshold for medium risk classification |

## Configuration Files

### Development Configuration (.env)

For local development, use the provided `.env.example` as a template:

```bash
cp .env.example .env
# Edit .env with your settings
```

### Production Configuration (.env.production)

For production deployment, use `.env.production.example` as a template:

```bash
cp .env.production.example .env.production
# Update all values with production settings
```

Key production considerations:
- Set `DEBUG=false`
- Use strong, unique tokens for `SECRET_KEY` and `BEARER_TOKEN`
- Configure appropriate `LOG_LEVEL` (WARNING or ERROR)
- Set restrictive `ALLOWED_ORIGINS`
- Use absolute paths for file storage directories

### Docker Configuration

When using Docker, pass environment variables via:

1. **Docker run command**:
```bash
docker run -p 8000:8000 \
  -e DEBUG=false \
  -e SECRET_KEY=your-secret-key \
  -e BEARER_TOKEN=your-bearer-token \
  thalassa
```

2. **Docker Compose** (docker-compose.yml):
```yaml
services:
  app:
    image: thalassa
    env_file:
      - .env.production
    ports:
      - "8000:8000"
```

3. **Kubernetes ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: thalassa-config
data:
  DEBUG: "false"
  ENVIRONMENT: "production"
  LOG_LEVEL: "WARNING"
```

## Environment-Specific Settings

### Development Environment

Optimized for debugging and rapid development:

```ini
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging Environment

Similar to production but with enhanced logging:

```ini
DEBUG=false
ENVIRONMENT=staging
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://staging.yourdomain.com
```

### Production Environment

Optimized for security and performance:

```ini
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://yourdomain.com
```

## Advanced Configuration

### Custom Configuration Module

The application loads configuration from `app/config.py`. You can extend this module for custom settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Add custom settings here
    custom_setting: str = "default_value"

    class Config:
        env_file = ".env"
```

### Runtime Configuration

Some settings can be modified at runtime via the admin API (requires authentication):

```bash
# Example: Update risk thresholds
curl -X PUT \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"critical_threshold": 0.85}' \
  http://localhost:8000/api/v1/admin/config
```

## Validation and Testing

### Validate Configuration

Test your configuration before deployment:

```bash
# Validate environment variables
pixi run python -c "from app.config import settings; print(settings.json(indent=2))"

# Test database connection (if configured)
pixi run python -c "from app.config import settings; settings.validate_database()"
```

### Configuration Health Check

The `/health` endpoint includes configuration validation:

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Missing Environment Variables

If required variables are missing:
```
ValueError: SECRET_KEY environment variable is required
```

Solution: Ensure all required variables are set in your `.env` file.

### Invalid Configuration Values

If configuration values are invalid:
```
ValidationError: BEARER_TOKEN must be at least 32 characters
```

Solution: Follow the validation requirements for each setting.

### File Permission Issues

If the application cannot write to configured directories:
```
PermissionError: [Errno 13] Permission denied: '/var/thalassa/uploads'
```

Solution: Ensure the application has write permissions:
```bash
sudo chown -R www-data:www-data /var/thalassa
chmod -R 755 /var/thalassa
```
