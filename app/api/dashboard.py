"""
Dashboard API endpoints for serving authenticated dashboard views.

This module provides endpoints for serving the dashboard HTML interface
to partners for viewing SRS risk assessment results.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..dependencies.auth import RequireAuth

router = APIRouter(prefix="/api/v1", tags=["dashboard"])

# Configure templates
templates = Jinja2Templates(directory="app/templates")


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
    # Prepare template context with placeholder data
    context = {
        "request": request,
        "filename": "Placeholder - No files processed yet",
        "risk_score": "Pending analysis setup",
        "status": "Dashboard template ready - awaiting data pipeline",
        "last_updated": "Template rendered successfully",
    }

    return templates.TemplateResponse("dashboard.html", context)


@router.get("/dashboard/health")
async def dashboard_health_check():
    """Health check endpoint for dashboard service."""
    return {
        "status": "healthy",
        "service": "dashboard",
        "template_support": "configured",
        "static_files": "mounted",
    }
