# Quick Start Guide

Get Project Thalassa up and running in minutes with this step-by-step guide.

## Prerequisites

Before you begin, ensure you have:
- [Pixi](https://pixi.sh/) package manager installed
- Git installed on your system
- A terminal/command line interface
- At least 1GB of free disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/IA-PieroCV/Project_Thalassa.git
cd Project_Thalassa
```

### 2. Install Pixi (if not already installed)

```bash
curl -fsSL https://pixi.sh/install.sh | bash
# Restart your terminal or source your shell profile
source ~/.bashrc  # or ~/.zshrc on macOS
```

### 3. Install Dependencies

```bash
pixi install
```

This command will:
- Create a virtual environment
- Install all Python dependencies
- Set up development tools

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred editor
nano .env  # or vim, code, etc.
```

Key settings to update:
- `BEARER_TOKEN`: Set a secure token for API authentication
- `SECRET_KEY`: Set a secure secret key for the application
- `DEBUG`: Set to `true` for development, `false` for production

### 5. Start the Application

```bash
pixi run dev
```

The application will start and be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Verify Installation

### Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-11T12:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### Test File Upload (with authentication)

```bash
# Replace YOUR_TOKEN with the BEARER_TOKEN from your .env file
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_data/sample.fastq" \
  http://localhost:8000/api/v1/upload
```

## Next Steps

- [Configuration Guide](configuration.md) - Detailed configuration options
- [API Overview](/user-guide/api-overview) - Complete API documentation
- [File Upload Guide](/user-guide/file-upload) - Detailed upload instructions
- [Docker Deployment](/development/docker) - Container deployment guide

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Change the PORT in your .env file
PORT=8001
# Restart the application
pixi run dev
```

### Permission Denied

If you encounter permission issues:
```bash
# Ensure the uploads and results directories are writable
chmod 755 uploads results logs
```

### Pixi Command Not Found

If pixi is not recognized after installation:
```bash
# Add pixi to your PATH
export PATH="$HOME/.pixi/bin:$PATH"
# Add to your shell profile for persistence
echo 'export PATH="$HOME/.pixi/bin:$PATH"' >> ~/.bashrc
```

## Getting Help

- Check the [documentation](https://ia-pierocv.github.io/Project_Thalassa)
- Report issues on [GitHub](https://github.com/IA-PieroCV/Project_Thalassa/issues)
- Review the [CHANGELOG](/changelog) for recent updates
