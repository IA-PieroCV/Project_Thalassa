# Contributing Guide

Thank you for your interest in contributing to Project Thalassa! This guide will help you get started with development.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Pixi package manager
- Git
- GitHub account

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/Project_Thalassa.git
   cd Project_Thalassa
   ```

2. **Set Up Development Environment**
   ```bash
   # Install pixi
   curl -fsSL https://pixi.sh/install.sh | bash

   # Install dependencies
   pixi install

   # Install pre-commit hooks
   pixi run pre-commit-install
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We use automated tools to maintain code quality:

- **Ruff**: For linting and formatting Python code
- **Black**: For consistent code formatting
- **MyPy**: For type checking
- **Pre-commit**: For automated checks before commits

Run quality checks:
```bash
# Format code
pixi run format

# Check formatting
pixi run format-check

# Lint code
pixi run lint

# Fix linting issues
pixi run lint-fix

# Type checking
pixi run typecheck

# Run all checks
pixi run check
```

### Writing Code

#### Python Style Guide

Follow PEP 8 with these additions:

```python
# Good: Use type hints
def calculate_risk_score(
    markers: list[float],
    weights: list[float]
) -> float:
    """Calculate weighted risk score.

    Args:
        markers: List of marker frequencies
        weights: List of marker weights

    Returns:
        Normalized risk score between 0.0 and 1.0
    """
    return sum(m * w for m, w in zip(markers, weights))

# Good: Use descriptive variable names
sequencing_depth = 30
risk_threshold = 0.8

# Bad: Single letter variables (except in comprehensions)
d = 30
t = 0.8
```

#### API Endpoints

New endpoints should follow RESTful conventions:

```python
from fastapi import APIRouter, Depends
from app.dependencies.auth import verify_token
from app.schemas.response import StandardResponse

router = APIRouter(prefix="/api/v1")

@router.get("/resource", response_model=StandardResponse)
async def get_resource(
    token: str = Depends(verify_token)
):
    """Get resource with proper authentication."""
    return StandardResponse(
        success=True,
        data={"resource": "data"},
        message="Resource retrieved successfully"
    )
```

### Testing

#### Writing Tests

All new features must include tests:

```python
# tests/unit/test_new_feature.py
import pytest
from app.services.new_feature import NewFeature

class TestNewFeature:
    """Test suite for NewFeature."""

    @pytest.fixture
    def feature(self):
        """Create feature instance for testing."""
        return NewFeature()

    def test_feature_initialization(self, feature):
        """Test feature initializes correctly."""
        assert feature is not None
        assert feature.status == "ready"

    def test_feature_process(self, feature):
        """Test feature processing."""
        result = feature.process("input")
        assert result == "expected_output"

    @pytest.mark.asyncio
    async def test_async_feature(self, feature):
        """Test async feature operations."""
        result = await feature.async_process()
        assert result is not None
```

#### Running Tests

```bash
# Run all tests
pixi run test

# Run with coverage
pixi run test-cov

# Run specific test file
pixi run pytest tests/unit/test_new_feature.py

# Run with verbose output
pixi run pytest -v

# Run only marked tests
pixi run pytest -m "not slow"
```

### Documentation

#### Code Documentation

Use Google-style docstrings:

```python
def complex_function(
    param1: str,
    param2: int,
    optional: bool = False
) -> dict[str, Any]:
    """Brief description of function.

    Longer description explaining the function's purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2
        optional: Description of optional parameter

    Returns:
        Description of return value structure

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer

    Examples:
        >>> result = complex_function("test", 42)
        >>> print(result["status"])
        "success"
    """
    pass
```

#### API Documentation

Document new endpoints in `docs/api/`:

```markdown
## New Endpoint

`POST /api/v1/new-endpoint`

Description of what the endpoint does.

### Request

**Headers:**
- `Authorization: Bearer TOKEN`
- `Content-Type: application/json`

**Body:**
```json
{
  "field1": "value1",
  "field2": 123
}
```

### Response

**Success (200):**
```json
{
  "success": true,
  "data": {
    "result": "value"
  }
}
```
```

## Commit Guidelines

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(upload): add batch upload support"
git commit -m "fix(auth): resolve token expiration issue"
git commit -m "docs(api): update endpoint documentation"
```

### Pre-commit Hooks

Pre-commit hooks run automatically:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

## Pull Request Process

### Creating a Pull Request

1. **Ensure Tests Pass**
   ```bash
   pixi run test
   pixi run check
   ```

2. **Update Documentation**
   - Update relevant docs
   - Add changelog entry
   - Update API docs if needed

3. **Create PR**
   ```bash
   git push origin feature/your-feature
   # Open PR on GitHub
   ```

4. **PR Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests added/updated
   ```

### Code Review

Reviews focus on:

1. **Functionality**: Does it work as intended?
2. **Tests**: Are tests comprehensive?
3. **Documentation**: Is it well-documented?
4. **Performance**: Any performance concerns?
5. **Security**: Any security issues?

## Project Structure

```
Project_Thalassa/
├── app/                # Application code
│   ├── api/           # API endpoints
│   ├── models/        # Data models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── tests/             # Test suite
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── fixtures/     # Test fixtures
├── docs/              # Documentation
├── scripts/           # Utility scripts
└── .github/           # GitHub workflows
```

## Development Commands

Quick reference:

```bash
# Development
pixi run dev           # Start dev server
pixi run analyze       # Run batch analysis

# Testing
pixi run test          # Run tests
pixi run test-cov      # Run with coverage

# Code Quality
pixi run format        # Format code
pixi run lint          # Lint code
pixi run typecheck     # Type checking
pixi run check         # All checks
pixi run fix          # Fix issues

# Documentation
pixi run docs-serve    # Serve docs locally
pixi run docs-build    # Build docs

# Utilities
pixi run clean         # Clean artifacts
```

## Getting Help

- **Discord**: [Join our Discord](https://discord.gg/thalassa)
- **Issues**: [GitHub Issues](https://github.com/IA-PieroCV/Project_Thalassa/issues)
- **Discussions**: [GitHub Discussions](https://github.com/IA-PieroCV/Project_Thalassa/discussions)
- **Email**: dev@thalassa.example.com

## License

By contributing, you agree that your contributions will be licensed under the project's license.
