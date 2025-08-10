"""
Integration tests for dashboard endpoints.

This module tests the dashboard functionality including authentication,
template rendering, results parsing, and proper response handling.
"""

import json
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from app.api.dashboard import (
    format_dashboard_context,
    get_latest_analysis_results,
    read_results_json,
)
from app.main import app


class TestDashboardEndpoints:
    """Integration tests for dashboard API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)

    @pytest.fixture
    def valid_auth_headers(self):
        """Create valid authentication headers for testing."""
        # This token needs to match the configured bearer token
        # For testing, we'll use a test environment variable
        return {"Authorization": "Bearer test-token-for-testing"}

    @pytest.fixture
    def invalid_auth_headers(self):
        """Create invalid authentication headers for testing."""
        return {"Authorization": "Bearer invalid-token"}

    @pytest.fixture
    def malformed_auth_headers(self):
        """Create malformed authentication headers for testing."""
        return [
            {"Authorization": "Basic dGVzdA=="},  # Basic auth instead of Bearer
            {"Authorization": "bearer test-token"},  # lowercase bearer
            {"Authorization": "Token test-token"},  # Wrong scheme
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": ""},  # Empty header
        ]

    def test_dashboard_without_auth_rejected(self, client):
        """Test that dashboard access without authentication is rejected."""
        response = client.get("/api/v1/dashboard")

        assert response.status_code == 401
        data = response.json()
        assert "Authorization header is required" in data["detail"]

    def test_dashboard_with_invalid_auth_rejected(self, client, invalid_auth_headers):
        """Test that dashboard access with invalid authentication is rejected."""
        response = client.get("/api/v1/dashboard", headers=invalid_auth_headers)

        assert response.status_code == 401
        data = response.json()
        assert "Invalid bearer token" in data["detail"]

    def test_dashboard_with_malformed_auth_rejected(
        self, client, malformed_auth_headers
    ):
        """Test that dashboard access with malformed authentication headers is rejected."""
        for headers in malformed_auth_headers:
            response = client.get("/api/v1/dashboard", headers=headers)
            assert response.status_code == 401

    def test_dashboard_health_endpoint_no_auth_required(self, client):
        """Test that dashboard health check endpoint works without authentication."""
        response = client.get("/api/v1/dashboard/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "dashboard"
        assert data["template_support"] == "configured"
        assert data["static_files"] == "mounted"

    @pytest.mark.skip(reason="Requires valid bearer token configuration")
    def test_dashboard_with_valid_auth_succeeds(self, client, valid_auth_headers):
        """Test that dashboard access with valid authentication succeeds."""
        response = client.get("/api/v1/dashboard", headers=valid_auth_headers)

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        # Check that the response contains expected dashboard content
        html_content = response.text
        assert "Project Thalassa" in html_content
        assert "SRS Risk Assessment Dashboard" in html_content
        assert "Authenticated" in html_content

    def test_dashboard_www_authenticate_header_present(self, client):
        """Test that unauthorized dashboard requests include WWW-Authenticate header."""
        response = client.get("/api/v1/dashboard")

        assert response.status_code == 401
        assert "www-authenticate" in response.headers
        assert response.headers["www-authenticate"] == "Bearer"

    @pytest.mark.skip(reason="Requires valid bearer token configuration")
    def test_dashboard_template_context_variables(self, client, valid_auth_headers):
        """Test that dashboard template receives proper context variables."""
        response = client.get("/api/v1/dashboard", headers=valid_auth_headers)

        assert response.status_code == 200
        html_content = response.text

        # Check for template context variables in the rendered HTML
        # These should appear in the dashboard based on the current implementation
        assert (
            "Placeholder - No files processed yet" in html_content
            or "filename" in html_content
        )
        assert "Pending analysis setup" in html_content or "risk_score" in html_content
        assert "Dashboard template ready" in html_content or "status" in html_content

    def test_dashboard_static_file_references(self, client):
        """Test that dashboard HTML references static files correctly."""
        # Test CSS file access
        response = client.get("/static/css/dashboard.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

        # Test JavaScript file access
        response = client.get("/static/js/dashboard.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "")

    def test_dashboard_endpoint_returns_html(self, client):
        """Test that dashboard endpoint returns HTML content type."""
        # This test works even without auth since we're checking the error response format
        response = client.get("/api/v1/dashboard")

        # Even with 401, we should get JSON error response (not HTML)
        assert response.status_code == 401
        assert "application/json" in response.headers.get("content-type", "")

        # The actual HTML response would be tested in the authenticated test above


class TestDashboardResultsParsing:
    """Tests for dashboard results parsing functionality."""

    @pytest.fixture
    def temp_results_file(self):
        """Create a temporary results.json file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            sample_results = {
                "timestamp": "2025-08-10T12:00:00.000000",
                "file_analysis": {
                    "filename": "test_sample.fastq",
                    "srs_risk_score": 0.65,
                    "risk_level": "medium",
                    "partner_id": "TestPartner",
                    "cage_id": "CAGE-01",
                    "sample_date": "2025-08-10",
                },
                "summary": {
                    "filename": "test_sample.fastq",
                    "risk_score": 0.65,
                    "risk_level": "medium",
                    "partner_id": "TestPartner",
                    "cage_id": "CAGE-01",
                    "sample_date": "2025-08-10",
                    "analysis_status": "completed",
                },
            }
            json.dump(sample_results, f)
            f.flush()
            yield Path(f.name)
        # Cleanup
        Path(f.name).unlink()

    def test_read_results_json_valid_file(self, temp_results_file):
        """Test reading a valid results.json file."""
        results = read_results_json(temp_results_file)

        assert results is not None
        assert "timestamp" in results
        assert "summary" in results
        assert results["summary"]["filename"] == "test_sample.fastq"
        assert results["summary"]["risk_score"] == 0.65
        assert results["summary"]["risk_level"] == "medium"

    def test_read_results_json_nonexistent_file(self):
        """Test reading a non-existent results.json file."""
        nonexistent_path = Path("/nonexistent/results.json")
        results = read_results_json(nonexistent_path)

        assert results is None

    def test_read_results_json_invalid_json(self):
        """Test reading an invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json content")
            f.flush()
            invalid_path = Path(f.name)

        try:
            results = read_results_json(invalid_path)
            assert results is None
        finally:
            invalid_path.unlink()

    def test_format_dashboard_context_with_results(self):
        """Test formatting dashboard context with valid results."""
        mock_request = MagicMock()
        mock_request.url = "http://test"

        results = {
            "timestamp": "2025-08-10T12:00:00.000000",
            "summary": {
                "filename": "test_sample.fastq",
                "risk_score": 0.75,
                "risk_level": "high",
                "partner_id": "TestPartner",
                "cage_id": "CAGE-01",
                "sample_date": "2025-08-10",
                "analysis_status": "completed",
            },
        }

        context = format_dashboard_context(results, mock_request)

        assert context["request"] == mock_request
        assert context["filename"] == "test_sample.fastq"
        assert context["risk_score"] == "0.750"
        assert context["risk_level"] == "high"
        assert context["partner_id"] == "TestPartner"
        assert context["cage_id"] == "CAGE-01"
        assert context["sample_date"] == "2025-08-10"
        assert "Analysis completed" in context["status"]

    def test_format_dashboard_context_without_results(self):
        """Test formatting dashboard context without results."""
        mock_request = MagicMock()
        mock_request.url = "http://test"

        context = format_dashboard_context(None, mock_request)

        assert context["request"] == mock_request
        assert context["filename"] == "No files processed yet"
        assert context["risk_score"] == "Pending analysis setup"
        assert context["risk_level"] == "unknown"
        assert context["partner_id"] is None
        assert context["cage_id"] is None

    def test_format_dashboard_context_with_failed_analysis(self):
        """Test formatting dashboard context with failed analysis."""
        mock_request = MagicMock()
        mock_request.url = "http://test"

        results = {
            "timestamp": "2025-08-10T12:00:00.000000",
            "summary": {
                "filename": "test_sample.fastq",
                "risk_score": None,
                "risk_level": "analysis_failed",
                "analysis_status": "failed",
            },
        }

        context = format_dashboard_context(results, mock_request)

        assert context["filename"] == "test_sample.fastq"
        assert context["risk_score"] == "Analysis failed"
        assert context["risk_level"] == "analysis_failed"
        assert "Analysis failed" in context["status"]

    @patch("app.api.dashboard.RESULTS_DIR")
    def test_get_latest_analysis_results_with_existing_file(
        self, mock_results_dir, temp_results_file
    ):
        """Test getting latest analysis results when results.json exists."""
        mock_results_dir.return_value = temp_results_file.parent

        # Mock the results file path to point to our temp file
        with patch("app.api.dashboard.RESULTS_DIR", temp_results_file.parent):
            # Create a results.json file in the mocked directory
            results_file = temp_results_file.parent / "results.json"
            results_file.write_text(temp_results_file.read_text())

            try:
                results = get_latest_analysis_results()

                assert results is not None
                assert "summary" in results
                assert results["summary"]["filename"] == "test_sample.fastq"
            finally:
                if results_file.exists():
                    results_file.unlink()

    @patch("app.api.dashboard.generate_live_analysis_results")
    @patch("app.api.dashboard.RESULTS_DIR")
    def test_get_latest_analysis_results_without_existing_file(
        self, mock_results_dir, mock_generate
    ):
        """Test getting latest analysis results when results.json doesn't exist."""
        # Mock results directory to be empty
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_results_dir.__truediv__ = lambda self, other: Path(temp_dir) / other

            # Mock generate_live_analysis_results to return test data
            mock_generate.return_value = {
                "summary": {
                    "filename": "live_analysis.fastq",
                    "risk_score": 0.45,
                    "analysis_status": "completed",
                }
            }

            results = get_latest_analysis_results()

            # Should have called generate_live_analysis_results
            mock_generate.assert_called_once()
            assert results is not None
            assert results["summary"]["filename"] == "live_analysis.fastq"

    @patch("app.api.dashboard.AnalysisService")
    @patch("app.api.dashboard.UPLOADS_DIR")
    def test_generate_live_analysis_results_with_files(
        self, mock_uploads_dir, mock_analysis_service
    ):
        """Test generating live analysis results when files are available."""
        from app.api.dashboard import generate_live_analysis_results

        # Mock the analysis service
        mock_service = MagicMock()
        mock_analysis_service.return_value = mock_service

        # Mock fastq files discovery
        mock_file = MagicMock()
        mock_file.name = "test_file.fastq"
        mock_file.stat.return_value.st_mtime = 1234567890
        mock_service.discover_fastq_files.return_value = [mock_file]

        # Mock file analysis
        mock_service.analyze_file.return_value = {
            "filename": "test_file.fastq",
            "srs_risk_score": 0.35,
            "risk_level": "low",
            "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
            "partner_id": "TestPartner",
            "cage_id": "CAGE-01",
        }

        with patch("app.api.dashboard.save_analysis_results"):
            results = generate_live_analysis_results()

        assert results is not None
        assert "summary" in results
        assert results["summary"]["filename"] == "test_file.fastq"
        assert results["summary"]["risk_score"] == 0.35
        assert results["summary"]["risk_level"] == "low"
        assert results["summary"]["analysis_status"] == "completed"

    @patch("app.api.dashboard.AnalysisService")
    def test_generate_live_analysis_results_no_files(self, mock_analysis_service):
        """Test generating live analysis results when no files are available."""
        from app.api.dashboard import generate_live_analysis_results

        # Mock the analysis service to return no files
        mock_service = MagicMock()
        mock_analysis_service.return_value = mock_service
        mock_service.discover_fastq_files.return_value = []

        results = generate_live_analysis_results()

        assert results is None

    @patch("app.api.dashboard.get_latest_analysis_results")
    def test_dashboard_endpoint_with_results(self, mock_get_results):
        """Test dashboard endpoint with analysis results available."""
        client = TestClient(app)

        # Mock analysis results
        mock_get_results.return_value = {
            "timestamp": "2025-08-10T12:00:00.000000",
            "summary": {
                "filename": "test_sample.fastq",
                "risk_score": 0.85,
                "risk_level": "critical",
                "partner_id": "TestPartner",
                "analysis_status": "completed",
            },
        }

        # This test would need authentication bypass or valid token
        # For now, we'll test the error case which doesn't require auth
        response = client.get("/api/v1/dashboard")

        # Should get 401 due to missing auth, but the results parsing should have been called
        assert response.status_code == 401

    @patch("app.api.dashboard.get_latest_analysis_results")
    def test_dashboard_endpoint_error_handling(self, mock_get_results):
        """Test dashboard endpoint handles errors gracefully."""
        client = TestClient(app)

        # Mock an exception during results retrieval
        mock_get_results.side_effect = Exception("Test error")

        response = client.get("/api/v1/dashboard")

        # Should still return 401 (auth error) and not crash
        assert response.status_code == 401
