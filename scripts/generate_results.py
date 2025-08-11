#!/usr/bin/env python3
"""
Batch analysis script to generate results.json file.

This script processes all FASTQ files in the uploads directory,
performs SRS risk analysis, and generates an aggregated results.json file
in the format required by the dashboard.
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Any

# Add the app directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.analysis import AnalysisService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function to process files and generate results.json."""
    try:
        # Configuration
        upload_dir = Path("uploads")
        results_dir = Path("results")
        results_file = results_dir / "results.json"

        logger.info("Starting batch analysis for results.json generation")
        logger.info(f"Upload directory: {upload_dir}")
        logger.info(f"Results file: {results_file}")

        # Ensure directories exist
        if not upload_dir.exists():
            logger.error(f"Upload directory does not exist: {upload_dir}")
            sys.exit(1)

        # Create results directory if it doesn't exist
        results_dir.mkdir(exist_ok=True)
        logger.info(f"Results directory ready: {results_dir}")

        # Initialize analysis service
        analysis_service = AnalysisService(upload_dir=str(upload_dir))

        # Discover all FASTQ files
        fastq_files = analysis_service.discover_fastq_files()
        logger.info(f"Discovered {len(fastq_files)} FASTQ files")

        if not fastq_files:
            logger.warning("No FASTQ files found - creating empty results.json")
            write_results_json([], results_file)
            return

        # Process each file and aggregate results
        aggregated_results = []
        processed_count = 0
        error_count = 0

        for file_path in fastq_files:
            try:
                logger.info(f"Processing file: {file_path.name}")

                # Perform comprehensive analysis
                file_analysis = analysis_service.analyze_file(file_path)

                # Extract required data for results.json format
                result_entry = extract_result_data(file_analysis)

                if result_entry:
                    aggregated_results.append(result_entry)
                    processed_count += 1
                    risk_score = result_entry.get("srsRiskScore", 0.0)
                    cage_id = result_entry.get("cageId", "unknown")

                    logger.info(
                        f"Successfully processed {file_path.name} - "
                        f"cage_id: {cage_id}, "
                        f"risk_score: {risk_score:.3f}"
                    )

                    # CRITICAL RISK ALERT: Check if risk score exceeds threshold
                    if risk_score >= settings.critical_risk_threshold:
                        print("\n" + "=" * 80)
                        print("🚨 CRITICAL RISK ALERT 🚨")
                        print("=" * 80)
                        print("HIGH RISK DETECTED - IMMEDIATE ATTENTION REQUIRED")
                        print("")
                        print(f"Cage ID: {cage_id}")
                        print(f"Risk Score: {risk_score:.3f}")
                        print(f"Threshold: {settings.critical_risk_threshold}")
                        print(f"File: {file_path.name}")
                        print(
                            f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                        print("")
                        print(
                            f"ACTION REQUIRED: Review operational procedures for Cage {cage_id}"
                        )
                        print("and implement appropriate risk mitigation measures.")
                        print("")
                        print(
                            "Please refer to the critical_alert_template.txt for email notification."
                        )
                        print("=" * 80)
                        print()

                        # Also log the critical alert to the logger
                        logger.critical(
                            f"CRITICAL RISK DETECTED - Cage {cage_id} has risk score "
                            f"{risk_score:.3f} (>= {settings.critical_risk_threshold}) - "
                            f"IMMEDIATE ACTION REQUIRED"
                        )
                else:
                    error_count += 1
                    logger.warning(f"Skipped {file_path.name} - missing required data")

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {file_path.name}: {e}")
                continue

        # Write results to JSON file
        write_results_json(aggregated_results, results_file)

        # Summary
        logger.info("Batch analysis complete")
        logger.info(f"Successfully processed: {processed_count} files")
        logger.info(f"Errors/skipped: {error_count} files")
        logger.info(f"Total results entries: {len(aggregated_results)}")
        logger.info(f"Results written to: {results_file}")

        if error_count > 0:
            logger.warning(f"Completed with {error_count} errors - check logs above")

    except Exception as e:
        logger.error(f"Fatal error in batch analysis: {e}")
        sys.exit(1)


def extract_result_data(file_analysis: dict[str, Any]) -> dict[str, Any] | None:
    """
    Extract the required data from file analysis results.

    Args:
        file_analysis: Complete analysis results from AnalysisService

    Returns:
        Dictionary in the format required by results.json or None if data is insufficient
    """
    try:
        # Required fields for results.json format
        cage_id = file_analysis.get("cage_id")
        srs_risk_score = file_analysis.get("srs_risk_score")
        risk_analysis_timestamp = file_analysis.get("risk_analysis_timestamp")

        # Validate required data is present
        if cage_id is None:
            logger.warning(
                f"Missing cage_id in analysis for {file_analysis.get('filename', 'unknown')}"
            )
            return None

        if srs_risk_score is None:
            logger.warning(
                f"Missing srs_risk_score in analysis for {file_analysis.get('filename', 'unknown')}"
            )
            return None

        # Use current timestamp if analysis timestamp is not available
        if not risk_analysis_timestamp:
            risk_analysis_timestamp = datetime.now().isoformat()
            logger.debug("Using current timestamp as lastUpdated")

        # Format according to required spec: [{ "cageId": "...", "srsRiskScore": ..., "lastUpdated": "..." }]
        return {
            "cageId": str(cage_id),
            "srsRiskScore": float(srs_risk_score),
            "lastUpdated": risk_analysis_timestamp,
        }

    except Exception as e:
        logger.error(f"Error extracting result data: {e}")
        return None


def write_results_json(results: list[dict[str, Any]], results_file: Path) -> None:
    """
    Write the aggregated results to results.json file.

    Args:
        results: List of result entries in the required format
        results_file: Path to the results.json file
    """
    try:
        # Ensure parent directory exists
        results_file.parent.mkdir(parents=True, exist_ok=True)

        # Write results to file (completely overwriting as required)
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully wrote {len(results)} entries to {results_file}")

    except Exception as e:
        logger.error(f"Error writing results to {results_file}: {e}")
        raise


if __name__ == "__main__":
    main()
