# Installation

This guide walks you through setting up Project Thalassa for development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - The platform requires Python 3.11+
- **Git** - For version control
- **Pixi** - Modern package manager (replaces conda/pip)

## Installing Pixi

Project Thalassa uses [Pixi](https://pixi.sh/) as its package manager, which provides fast, reproducible environments with both conda and PyPI packages.

=== "Linux/macOS"

    ```bash
    curl -fsSL https://pixi.sh/install.sh | bash
    ```

=== "Windows"

    ```powershell
    iwr -useb https://pixi.sh/install.ps1 | iex
    ```

After installation, restart your terminal or source your shell profile.

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd salmon
```

### 2. Install Dependencies

Pixi will automatically create an isolated environment with all required dependencies:

```bash
pixi install
```

This installs:

- **Runtime dependencies** - FastAPI, Uvicorn, data science libraries
- **Development tools** - pytest, ruff, ty (type checker)
- **Bioinformatics packages** - BioPython and related tools

### 3. Environment Configuration

Copy the environment template and customize:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```bash
# Application Settings
APP_NAME="Project Thalassa"
DEBUG=true
ENVIRONMENT="development"

# File Storage (customize paths)
UPLOAD_DIR="uploads"
RESULTS_DIR="results"
MAX_FILE_SIZE_MB=100

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 4. Verify Installation

Test that everything is working:

```bash
# Run quality checks
pixi run check

# Run tests
pixi run test

# Start development server
pixi run dev
```

Visit `http://localhost:8000/docs` to see the interactive API documentation.

## Development Tools

The project includes several development commands:

| Command | Description |
|---------|-------------|
| `pixi run dev` | Start development server with auto-reload |
| `pixi run test` | Run the test suite |
| `pixi run test-cov` | Run tests with coverage report |
| `pixi run check` | Run all quality checks (lint, format, type) |
| `pixi run format` | Format code with ruff |
| `pixi run lint` | Lint code with ruff |
| `pixi run typecheck` | Type check with ty |

## IDE Setup

### VS Code

Recommended extensions:

- **Python** - Microsoft's Python extension
- **Ruff** - Linting and formatting
- **Material Icon Theme** - Better file icons

The project includes `.vscode/settings.json` with optimal configurations.

### PyCharm

Configure PyCharm to use the pixi environment:

1. Go to **Settings** → **Project** → **Python Interpreter**
2. Add interpreter from pixi environment: `.pixi/envs/default/bin/python`

## Next Steps

- [Quick Start](quickstart.md) - Run your first API request
- [Configuration](configuration.md) - Detailed configuration options
- [Development Guide](../development/contributing.md) - Start contributing
