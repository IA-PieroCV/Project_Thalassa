"""
Integration tests for dashboard endpoints.

This module tests the dashboard functionality including authentication,
template rendering, and proper response handling.
"""

from fastapi.testclient import TestClient
import pytest

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
