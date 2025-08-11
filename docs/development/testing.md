# Testing Guide

Comprehensive testing ensures Project Thalassa remains reliable and maintainable.

## Testing Philosophy

We follow these principles:
- **Test-Driven Development (TDD)** for new features
- **High coverage** (>80%) for critical paths
- **Fast feedback** with unit tests
- **Realistic scenarios** with integration tests
- **Automated testing** in CI/CD pipeline

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_main.py         # Main app tests
├── unit/                # Unit tests
│   ├── test_*.py       # Individual unit tests
│   └── __init__.py
├── integration/         # Integration tests
│   ├── test_*.py       # Integration tests
│   └── __init__.py
└── fixtures/           # Test data
    ├── sample.fastq    # Sample files
    └── __init__.py
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pixi run test

# Run with coverage report
pixi run test-cov

# Run specific test file
pixi run pytest tests/unit/test_auth_service.py

# Run specific test
pixi run pytest tests/unit/test_auth_service.py::test_token_validation

# Run tests matching pattern
pixi run pytest -k "auth"

# Run with verbose output
pixi run pytest -v

# Run with detailed failure info
pixi run pytest --tb=short
```

### Test Markers

```bash
# Run only fast tests
pixi run pytest -m "not slow"

# Run only integration tests
pixi run pytest -m "integration"

# Run only unit tests
pixi run pytest tests/unit/
```

## Writing Tests

### Unit Tests

Unit tests verify individual components in isolation:

```python
# tests/unit/test_risk_calculator.py
import pytest
from app.services.risk_calculator import RiskCalculator

class TestRiskCalculator:
    """Test suite for RiskCalculator service."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return RiskCalculator()

    def test_calculate_basic_score(self, calculator):
        """Test basic risk score calculation."""
        markers = [0.5, 0.7, 0.3]
        weights = [0.3, 0.5, 0.2]

        score = calculator.calculate_score(markers, weights)

        assert score == pytest.approx(0.54, rel=1e-2)
        assert 0.0 <= score <= 1.0

    def test_normalize_score(self, calculator):
        """Test score normalization."""
        raw_score = 2.5

        normalized = calculator.normalize(raw_score)

        assert normalized == 1.0  # Capped at maximum

    def test_invalid_inputs(self, calculator):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError, match="Mismatched lengths"):
            calculator.calculate_score([0.5], [0.3, 0.7])

        with pytest.raises(ValueError, match="Invalid marker value"):
            calculator.calculate_score([-0.1], [0.5])

    @pytest.mark.parametrize("markers,weights,expected", [
        ([0.0, 0.0], [0.5, 0.5], 0.0),
        ([1.0, 1.0], [0.5, 0.5], 1.0),
        ([0.5, 0.5], [0.6, 0.4], 0.5),
    ])
    def test_score_calculations(self, calculator, markers, weights, expected):
        """Test various score calculations."""
        score = calculator.calculate_score(markers, weights)
        assert score == pytest.approx(expected, rel=1e-2)
```

### Integration Tests

Integration tests verify components work together:

```python
# tests/integration/test_upload_workflow.py
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile

from app.main import app

class TestUploadWorkflow:
    """Test complete upload workflow."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers."""
        return {"Authorization": "Bearer test-token"}

    @pytest.fixture
    def sample_file(self):
        """Create sample FASTQ file."""
        content = "@SEQ_ID\nGATTACA\n+\n!!!!!!!!"
        with tempfile.NamedTemporaryFile(
            suffix=".fastq",
            delete=False
        ) as f:
            f.write(content.encode())
            return Path(f.name)

    def test_complete_upload_workflow(
        self, client, auth_headers, sample_file
    ):
        """Test complete file upload and processing."""
        # Upload file
        with open(sample_file, "rb") as f:
            response = client.post(
                "/api/v1/upload",
                headers=auth_headers,
                files={"file": ("test.fastq", f, "application/octet-stream")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "File uploaded successfully"

        # Verify file listed
        response = client.get(
            "/api/v1/upload/files",
            headers=auth_headers
        )
        assert response.status_code == 200
        files = response.json()["files"]
        assert len(files) > 0

        # Check dashboard reflects upload
        response = client.get(
            "/api/v1/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "test.fastq" in response.text
```

### Async Tests

Testing async functions:

```python
# tests/unit/test_async_service.py
import pytest
import asyncio
from app.services.async_processor import AsyncProcessor

class TestAsyncProcessor:
    """Test async processing service."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return AsyncProcessor()

    @pytest.mark.asyncio
    async def test_async_processing(self, processor):
        """Test async file processing."""
        result = await processor.process_file("test.fastq")

        assert result["status"] == "completed"
        assert result["duration"] > 0

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, processor):
        """Test concurrent file processing."""
        files = ["file1.fastq", "file2.fastq", "file3.fastq"]

        tasks = [processor.process_file(f) for f in files]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, processor):
        """Test processing timeout."""
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                processor.process_large_file("huge.fastq"),
                timeout=1.0
            )
```

## Test Fixtures

### Shared Fixtures

Define in `conftest.py`:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
from pathlib import Path

from app.main import app
from app.config import settings

@pytest.fixture(scope="session")
def test_client():
    """Create test client for entire session."""
    return TestClient(app)

@pytest.fixture(scope="function")
def temp_upload_dir():
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = tmpdir
        yield Path(tmpdir)
        settings.UPLOAD_DIR = original

@pytest.fixture
def mock_auth(monkeypatch):
    """Mock authentication for testing."""
    def mock_verify(*args, **kwargs):
        return {"user": "test", "role": "admin"}

    monkeypatch.setattr(
        "app.dependencies.auth.verify_token",
        mock_verify
    )

@pytest.fixture
def sample_fastq_content():
    """Sample FASTQ file content."""
    return """@SEQ_ID_1
GATCGATCGATCGATC
+
IIIIIIIIIIIIIIII
@SEQ_ID_2
ATCGATCGATCGATCG
+
HHHHHHHHHHHHHHHH"""

@pytest.fixture
def valid_filename():
    """Valid FASTQ filename."""
    return "Mowi_CAGE-04B_2025-08-15_S01.fastq"
```

### Using Fixtures

```python
def test_with_fixtures(
    test_client,
    temp_upload_dir,
    mock_auth,
    sample_fastq_content
):
    """Test using multiple fixtures."""
    # Create test file
    test_file = temp_upload_dir / "test.fastq"
    test_file.write_text(sample_fastq_content)

    # Test with mocked auth
    response = test_client.post("/api/v1/upload")
    assert response.status_code == 200
```

## Mocking

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """Test with mocked dependencies."""
    # Create mock
    mock_service = Mock()
    mock_service.process.return_value = {"result": "success"}

    # Use mock
    result = mock_service.process("input")
    assert result["result"] == "success"
    mock_service.process.assert_called_once_with("input")

@patch("app.services.external_api.requests.get")
def test_external_api(mock_get):
    """Test with patched external call."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    from app.services.external_api import fetch_data
    result = fetch_data()

    assert result["data"] == "test"
    mock_get.assert_called_once()
```

### Using pytest-mock

```python
def test_with_pytest_mock(mocker):
    """Test using pytest-mock."""
    mock_func = mocker.patch("app.services.calculator.complex_calculation")
    mock_func.return_value = 42

    from app.services.calculator import calculate
    result = calculate()

    assert result == 42
    mock_func.assert_called_once()
```

## Coverage

### Running Coverage

```bash
# Run tests with coverage
pixi run test-cov

# Generate HTML report
pixi run pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# pyproject.toml or .coveragerc
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
precision = 2
show_missing = true
skip_covered = false
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import requests

def make_request(url, headers):
    """Make single request."""
    return requests.get(url, headers=headers)

@pytest.mark.slow
def test_concurrent_requests():
    """Test handling concurrent requests."""
    url = "http://localhost:8000/health"
    headers = {"Authorization": "Bearer test"}
    num_requests = 100

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(make_request, url, headers)
            for _ in range(num_requests)
        ]
        results = [f.result() for f in futures]

    duration = time.time() - start_time

    assert all(r.status_code == 200 for r in results)
    assert duration < 10  # Should complete within 10 seconds

    print(f"Processed {num_requests} requests in {duration:.2f}s")
    print(f"Rate: {num_requests/duration:.2f} req/s")
```

### Profiling

```python
# tests/performance/test_profile.py
import cProfile
import pstats
from io import StringIO

def test_profile_processing():
    """Profile processing performance."""
    profiler = cProfile.Profile()

    profiler.enable()
    # Run code to profile
    result = expensive_operation()
    profiler.disable()

    # Print stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)

    print(s.getvalue())
    assert result is not None
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Install Pixi
      run: |
        curl -fsSL https://pixi.sh/install.sh | bash
        echo "$HOME/.pixi/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: pixi install

    - name: Run tests
      run: pixi run test-cov

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Organization

1. **One test class per module**
2. **Descriptive test names**
3. **Arrange-Act-Assert pattern**
4. **Minimal test dependencies**
5. **Fast unit tests (<100ms)**

### Test Data

1. **Use fixtures for reusable data**
2. **Create minimal test cases**
3. **Clean up after tests**
4. **Avoid hardcoded values**
5. **Use factories for complex objects**

### Assertions

```python
# Good: Specific assertions
assert response.status_code == 200
assert "error" not in response.json()
assert len(results) == expected_count

# Good: Helpful error messages
assert score > 0, f"Score {score} should be positive"

# Good: Use pytest.approx for floats
assert value == pytest.approx(3.14, rel=1e-2)

# Bad: Generic assertions
assert response
assert results
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pixi run pytest -s

# Show local variables on failure
pixi run pytest -l

# Drop into debugger on failure
pixi run pytest --pdb

# Stop on first failure
pixi run pytest -x
```

### Using pdb

```python
def test_with_debugger():
    """Test with debugger."""
    import pdb; pdb.set_trace()
    result = complex_function()
    assert result == expected
```

## Test Documentation

Document complex test scenarios:

```python
def test_complex_scenario():
    """Test handling of edge case in risk calculation.

    This test verifies that when multiple high-risk markers
    are present but with low confidence scores, the system
    correctly applies confidence weighting to prevent false
    positives.

    Scenario:
    - 3 high-risk markers (>0.8)
    - Low confidence (<0.5)
    - Expected: Medium risk classification
    """
    # Test implementation
    pass
```
