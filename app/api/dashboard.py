"""
Dashboard API endpoints for serving authenticated dashboard views.

This module provides endpoints for serving the dashboard HTML interface
to partners for viewing SRS risk assessment results.
"""

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import settings
from ..dependencies.auth import RequireAuth
from ..services.analysis import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["dashboard"])

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Configure results directory
RESULTS_DIR = Path("results")
UPLOADS_DIR = Path("uploads")


def read_results_json(results_path: Path) -> dict[str, Any] | None:
    """
    Read and parse a results.json file.

    Args:
        results_path: Path to the results.json file

    Returns:
        Parsed results data or None if file doesn't exist or is invalid
    """
    if not results_path.exists():
        logger.warning(f"Results file not found: {results_path}")
        return None

    try:
        with open(results_path, encoding="utf-8") as f:
            results_data = json.load(f)
        logger.debug(f"Successfully loaded results from {results_path}")
        return results_data
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading results file {results_path}: {e}")
        return None


def get_latest_analysis_results() -> dict[str, Any] | None:
    """
    Get the latest analysis results by checking for results.json files.

    This function looks for results.json in the results directory,
    and if not found, performs live analysis on uploaded files.

    Returns:
        Latest analysis results or None if no results available
    """
    # First, try to find existing results.json
    results_file = RESULTS_DIR / "results.json"
    if results_file.exists():
        return read_results_json(results_file)

    # If no results.json exists, perform live analysis on uploaded files
    return generate_live_analysis_results()


def generate_live_analysis_results() -> dict[str, Any] | None:
    """
    Generate live analysis results from uploaded files.

    This function uses the AnalysisService to analyze uploaded files
    and generate fresh results when results.json doesn't exist.

    Returns:
        Generated analysis results or None if no files to analyze
    """
    try:
        analysis_service = AnalysisService(upload_dir=str(UPLOADS_DIR))

        # Get all uploaded files
        fastq_files = analysis_service.discover_fastq_files()
        if not fastq_files:
            logger.info("No FASTQ files found for analysis")
            return None

        # Analyze the most recent file
        latest_file = max(fastq_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Analyzing latest file: {latest_file.name}")

        # Perform comprehensive analysis
        file_analysis = analysis_service.analyze_file(latest_file)

        # Format results for dashboard consumption
        results = {
            "timestamp": file_analysis.get("risk_analysis_timestamp"),
            "file_analysis": file_analysis,
            "summary": {
                "filename": file_analysis.get("filename"),
                "risk_score": file_analysis.get("srs_risk_score", 0.0),
                "risk_level": file_analysis.get("risk_level", "unknown"),
                "partner_id": file_analysis.get("partner_id"),
                "cage_id": file_analysis.get("cage_id"),
                "sample_date": file_analysis.get("sample_date"),
                "analysis_status": "completed"
                if file_analysis.get("srs_risk_score") is not None
                else "failed",
            },
        }

        # Optionally save results for future use
        save_analysis_results(results)

        return results

    except Exception as e:
        logger.error(f"Error generating live analysis results: {e}")
        return None


def save_analysis_results(results: dict[str, Any]) -> None:
    """
    Save analysis results to results.json for future dashboard loads.

    Args:
        results: Analysis results to save
    """
    try:
        # Ensure results directory exists
        RESULTS_DIR.mkdir(exist_ok=True)

        results_file = RESULTS_DIR / "results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results saved to {results_file}")

    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Error saving analysis results: {e}")


def format_dashboard_context(
    results: dict[str, Any] | None, request: Request
) -> dict[str, Any]:
    """
    Format analysis results into dashboard template context.

    Args:
        results: Analysis results data or None
        request: FastAPI request object

    Returns:
        Template context dictionary
    """
    if not results:
        # Return placeholder context when no results available
        return {
            "request": request,
            "filename": "No files processed yet",
            "risk_score": "Pending analysis setup",
            "risk_level": "unknown",
            "status": "Dashboard template ready - awaiting data pipeline",
            "last_updated": "Template rendered successfully",
            "partner_id": None,
            "cage_id": None,
            "sample_date": None,
            "analysis_error": None,
            "app_version": settings.app_version,
        }

    # Handle both new format (with summary) and simple results.json array format
    if isinstance(results, list) and results:
        # Handle simple results.json format (array of cage results)
        # Sort by lastUpdated timestamp to get most recent first
        sorted_results = sorted(
            results, key=lambda x: x.get("lastUpdated", ""), reverse=True
        )

        # Calculate summary statistics for all results
        total_results = len(sorted_results)
        high_risk_count = sum(1 for r in results if r.get("srsRiskScore", 0) >= 0.7)
        medium_risk_count = sum(
            1 for r in results if 0.3 <= r.get("srsRiskScore", 0) < 0.7
        )
        low_risk_count = sum(1 for r in results if r.get("srsRiskScore", 0) < 0.3)

        # Get unique cage IDs
        unique_cages = list({r.get("cageId") for r in results if r.get("cageId")})

        # Determine overall risk level based on highest risk in batch
        max_risk_score = max(r.get("srsRiskScore", 0) for r in results)
        if max_risk_score >= 0.7:
            overall_risk_level = "high"
        elif max_risk_score >= 0.3:
            overall_risk_level = "medium"
        else:
            overall_risk_level = "low"

        # Prepare all results for template display
        formatted_results = []
        for result in sorted_results:
            risk_score = result.get("srsRiskScore", 0.0)
            cage_id = result.get("cageId")
            last_updated = result.get("lastUpdated", "Unknown")

            # Determine individual risk level
            if risk_score >= 0.7:
                risk_level = "high"
            elif risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"

            formatted_results.append(
                {
                    "cage_id": cage_id,
                    "risk_score": f"{risk_score:.3f}",
                    "risk_level": risk_level,
                    "last_updated": last_updated,
                    "numeric_risk_score": risk_score,
                }
            )

        return {
            "request": request,
            "filename": f"Batch Analysis Results ({total_results} samples)",
            "risk_score": f"{max_risk_score:.3f}",
            "risk_level": overall_risk_level,
            "status": f"Analysis completed - {total_results} samples processed",
            "last_updated": sorted_results[0].get("lastUpdated", "Unknown"),
            "partner_id": None,
            "cage_id": f"{len(unique_cages)} cages monitored",
            "sample_date": None,
            "analysis_error": None,
            # New fields for multi-entry display
            "all_results": formatted_results,
            "total_results": total_results,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            "unique_cages": unique_cages,
            "has_multiple_results": True,
            "app_version": settings.app_version,
        }

    # Handle new format with summary structure
    if results.get("summary"):
        summary = results["summary"]

        # Format risk score for display
        risk_score = summary.get("risk_score")
        if isinstance(risk_score, float):
            risk_score_display = f"{risk_score:.3f}"
        else:
            risk_score_display = "Analysis failed"

        # Determine status message
        analysis_status = summary.get("analysis_status", "unknown")
        if analysis_status == "completed":
            status = f"Analysis completed - Risk level: {summary.get('risk_level', 'unknown')}"
        elif analysis_status == "failed":
            status = "Analysis failed - Please check file format"
        else:
            status = "Analysis status unknown"

        return {
            "request": request,
            "filename": summary.get("filename", "Unknown file"),
            "risk_score": risk_score_display,
            "risk_level": summary.get("risk_level", "unknown"),
            "status": status,
            "last_updated": results.get("timestamp", "Unknown"),
            "partner_id": summary.get("partner_id"),
            "cage_id": summary.get("cage_id"),
            "sample_date": summary.get("sample_date"),
            "analysis_error": summary.get("analysis_error"),
            "app_version": settings.app_version,
        }

    # Fallback for unexpected format
    return {
        "request": request,
        "filename": "Unknown format",
        "risk_score": "Format error",
        "risk_level": "unknown",
        "status": "Unexpected results format",
        "last_updated": "Unknown",
        "partner_id": None,
        "cage_id": None,
        "sample_date": None,
        "analysis_error": "Results format not recognized",
        "app_version": settings.app_version,
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    _: RequireAuth = None,
):
    """
    Serve the authenticated dashboard HTML interface.

    This endpoint serves the main dashboard interface for partners
    to view SRS risk assessment results. It reads and parses results.json
    files or performs live analysis on uploaded FASTQ files.

    Authentication: Bearer token required in Authorization header.
    """
    logger.info("Dashboard access requested")

    # Get the latest analysis results
    try:
        results = get_latest_analysis_results()
        logger.debug(f"Retrieved analysis results: {results is not None}")
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {e}")
        results = None

    # Format results for template context
    context = format_dashboard_context(results, request)

    logger.info(f"Serving dashboard for file: {context.get('filename')}")
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
