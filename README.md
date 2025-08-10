# Project Thalassa

A bioinformatics data analysis platform for SRS risk assessment, built with FastAPI and Python.

## Quick Start

### Prerequisites

- [Pixi](https://pixi.sh/) package manager (replaces conda/pip)
- Git

### Development Setup

1. **Clone the repository and navigate to the project directory:**

   ```bash
   git clone <repository-url>
   cd salmon
   ```

2. **Install pixi (if not already installed):**

   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   # Restart your terminal or source your shell profile
   ```

3. **Install dependencies and set up environment:**

   ```bash
   pixi install
   ```

4. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**

   ```bash
   pixi run dev
   ```

   The API will be available at `http://localhost:8000`
   Interactive API documentation at `http://localhost:8000/docs`

### Development Commands

- **Run the development server:** `pixi run dev`
- **Run tests:** `pixi run test`
- **Run tests with coverage:** `pixi run test-cov`
- **Format code:** `pixi run format`
- **Check formatting:** `pixi run format-check`
- **Lint code:** `pixi run lint`
- **Fix linting issues:** `pixi run lint-fix`
- **Type checking:** `pixi run typecheck`
- **Run all quality checks:** `pixi run check`
- **Fix formatting and linting:** `pixi run fix`
- **Clean build artifacts:** `pixi run clean`

### Docker Deployment

```bash
# Build the container
docker build -t thalassa .

# Run the container
docker run -p 8000:8000 thalassa
```

### Documentation

View and contribute to project documentation:

```bash
# Serve documentation locally
pixi run --environment docs docs-serve

# Build static documentation
pixi run --environment docs docs-build
```

Visit `http://localhost:8000` to view the documentation.

## Project Structure

```
salmon/
├── app/                    # Application source code
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── api/               # API route modules
│   ├── models/            # Data models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures
├── docs/                  # Project documentation
├── uploads/               # File upload directory (configurable)
├── results/               # Analysis results directory (configurable)
├── pixi.toml             # Pixi project configuration and dependencies
├── pixi.lock             # Locked dependency versions (auto-generated)
├── ruff.toml             # Ruff linter and formatter configuration
├── Dockerfile            # Container configuration
└── .env.example          # Environment variables template
```

## Development Toolchain

This project uses a modern Python development stack:

- **Package Manager:** [Pixi](https://pixi.sh/) - Fast, cross-platform package manager
- **Linting & Formatting:** [Ruff](https://docs.astral.sh/ruff/) - Extremely fast Python linter and formatter
- **Type Checking:** [Ty](https://github.com/adamchainz/ty) - Fast type checker
- **Testing:** [pytest](https://pytest.org/) with async support and coverage reporting
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn server

## Epics and User Stories

### Epic: Data Ingestion and Processing (ID: 173)

- **Story:** Partner provides sequence data via a shared folder (ID: 174)
- **Story:** Analyst generates risk score from data (ID: 175)

### Epic: Risk Reporting & Alerting (ID: 176)

- **Story:** Partner accesses dashboard with a password (ID: 177)
- **Story:** Partner views risk scores on the dashboard (ID: 178)
- **Story:** Analyst manually alerts partner of critical risk (ID: 179)
