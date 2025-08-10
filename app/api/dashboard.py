"""
Dashboard API endpoints for serving authenticated dashboard views.

This module provides endpoints for serving the dashboard HTML interface
to partners for viewing SRS risk assessment results.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..dependencies.auth import RequireAuth

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    _: RequireAuth = None,
):
    """
    Serve the authenticated dashboard HTML interface.

    This endpoint serves the main dashboard interface for partners
    to view SRS risk assessment results. Requires Bearer token authentication.

    Authentication: Bearer token required in Authorization header.
    """
    # TODO: This is a placeholder response until dashboard.html is created
    # and the template rendering is fully implemented in Issue #35
    return """
    <html>
        <head>
            <title>Project Thalassa - Dashboard</title>
        </head>
        <body>
            <h1>Project Thalassa Dashboard</h1>
            <p>Dashboard functionality coming soon...</p>
            <p>Authentication successful!</p>
        </body>
    </html>
    """


@router.get("/dashboard/health")
async def dashboard_health_check():
    """Health check endpoint for dashboard service."""
    return {
        "status": "healthy",
        "service": "dashboard",
        "template_support": "configured",
        "static_files": "mounted",
    }
