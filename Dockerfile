# Multi-stage build for optimized production image
FROM ghcr.io/prefix-dev/pixi:0.41.4 AS build

WORKDIR /app

# Set environment variables for build stage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy pixi configuration files
COPY pixi.toml pixi.lock ./

# Install dependencies to /app/.pixi/envs/prod
# Use --locked to ensure lockfile is up to date with pixi.toml
RUN pixi install --locked -e prod

# Create shell-hook activation script for production environment
RUN pixi shell-hook -e prod -s bash > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
RUN echo 'exec "$@"' >> /app/entrypoint.sh

# Production stage with minimal Ubuntu base
FROM ubuntu:24.04 AS production

WORKDIR /app

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy only the production environment (keep the same prefix path)
COPY --from=build /app/.pixi/envs/prod /app/.pixi/envs/prod

# Copy entrypoint script with proper permissions
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh

# Copy application code
COPY app/ ./app/

# Copy scripts directory for analysis functionality
COPY scripts/ ./scripts/

# Copy environment configuration template
COPY .env.example ./

# Create necessary directories for application runtime
RUN mkdir -p uploads results logs \
    && chmod 755 uploads results logs

# Create non-root user for security
RUN groupadd -r thalassa && useradd -r -g thalassa thalassa \
    && chown -R thalassa:thalassa /app

# Switch to non-root user
USER thalassa

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint to activate pixi environment and run command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
