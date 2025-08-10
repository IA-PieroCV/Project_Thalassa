"""
Unit tests for the generate_results.py script.

Tests the batch analysis script functionality including
result data extraction, JSON formatting, and error handling.
"""

import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest

# Import the functions we want to test
from scripts.generate_results import extract_result_data, write_results_json


class TestExtractResultData:
    """Test the extract_result_data function."""

    def test_extract_valid_data(self):
        """Test extracting valid result data."""
        file_analysis = {
            "filename": "test_file.fastq",
            "cage_id": "CAGE-01A",
            "srs_risk_score": 0.75,
            "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
        }

        result = extract_result_data(file_analysis)

        assert result is not None
        assert result["cageId"] == "CAGE-01A"
        assert result["srsRiskScore"] == 0.75
        assert result["lastUpdated"] == "2025-08-10T12:00:00.000000"

    def test_extract_data_missing_cage_id(self):
        """Test extracting data when cage_id is missing."""
        file_analysis = {
            "filename": "test_file.fastq",
            "srs_risk_score": 0.75,
            "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
        }

        result = extract_result_data(file_analysis)
        assert result is None

    def test_extract_data_missing_risk_score(self):
        """Test extracting data when srs_risk_score is missing."""
        file_analysis = {
            "filename": "test_file.fastq",
            "cage_id": "CAGE-01A",
            "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
        }

        result = extract_result_data(file_analysis)
        assert result is None

    def test_extract_data_missing_timestamp_uses_current(self):
        """Test extracting data when timestamp is missing uses current time."""
        file_analysis = {
            "filename": "test_file.fastq",
            "cage_id": "CAGE-01A",
            "srs_risk_score": 0.75,
        }

        with patch("scripts.generate_results.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2025-08-10T15:30:00.000000"
            )

            result = extract_result_data(file_analysis)

            assert result is not None
            assert result["cageId"] == "CAGE-01A"
            assert result["srsRiskScore"] == 0.75
            assert result["lastUpdated"] == "2025-08-10T15:30:00.000000"

    def test_extract_data_handles_string_numeric_values(self):
        """Test that numeric values are properly converted to expected types."""
        file_analysis = {
            "filename": "test_file.fastq",
            "cage_id": 123,  # Integer cage_id
            "srs_risk_score": "0.85",  # String risk score
            "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
        }

        result = extract_result_data(file_analysis)

        assert result is not None
        assert result["cageId"] == "123"  # Converted to string
        assert result["srsRiskScore"] == 0.85  # Converted to float
        assert isinstance(result["cageId"], str)
        assert isinstance(result["srsRiskScore"], float)

    def test_extract_data_handles_exception(self):
        """Test that extraction handles exceptions gracefully."""
        file_analysis = {
            "cage_id": "CAGE-01A",
            "srs_risk_score": "not_a_number",  # Invalid float
        }

        result = extract_result_data(file_analysis)
        assert result is None


class TestWriteResultsJson:
    """Test the write_results_json function."""

    def test_write_valid_results(self):
        """Test writing valid results to JSON file."""
        results = [
            {
                "cageId": "CAGE-01A",
                "srsRiskScore": 0.75,
                "lastUpdated": "2025-08-10T12:00:00.000000",
            },
            {
                "cageId": "CAGE-02B",
                "srsRiskScore": 0.25,
                "lastUpdated": "2025-08-10T12:01:00.000000",
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            results_file = Path(temp_dir) / "results.json"

            write_results_json(results, results_file)

            # Verify file was created and has correct content
            assert results_file.exists()

            with open(results_file, encoding="utf-8") as f:
                written_data = json.load(f)

            assert len(written_data) == 2
            assert written_data[0]["cageId"] == "CAGE-01A"
            assert written_data[0]["srsRiskScore"] == 0.75
            assert written_data[1]["cageId"] == "CAGE-02B"
            assert written_data[1]["srsRiskScore"] == 0.25

    def test_write_empty_results(self):
        """Test writing empty results list."""
        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            results_file = Path(temp_dir) / "results.json"

            write_results_json(results, results_file)

            assert results_file.exists()

            with open(results_file, encoding="utf-8") as f:
                written_data = json.load(f)

            assert written_data == []

    def test_write_creates_parent_directory(self):
        """Test that writing creates parent directories if they don't exist."""
        results = [
            {
                "cageId": "TEST",
                "srsRiskScore": 0.5,
                "lastUpdated": "2025-08-10T12:00:00",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "directory" / "results.json"

            write_results_json(results, nested_path)

            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_write_overwrites_existing_file(self):
        """Test that writing completely overwrites existing file."""
        initial_results = [
            {"cageId": "OLD", "srsRiskScore": 0.1, "lastUpdated": "2025-01-01T00:00:00"}
        ]
        new_results = [
            {"cageId": "NEW", "srsRiskScore": 0.9, "lastUpdated": "2025-08-10T12:00:00"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            results_file = Path(temp_dir) / "results.json"

            # Write initial data
            write_results_json(initial_results, results_file)

            # Overwrite with new data
            write_results_json(new_results, results_file)

            # Verify only new data exists
            with open(results_file, encoding="utf-8") as f:
                written_data = json.load(f)

            assert len(written_data) == 1
            assert written_data[0]["cageId"] == "NEW"

    def test_write_handles_permission_error(self):
        """Test that write function handles permission errors."""
        results = [
            {
                "cageId": "TEST",
                "srsRiskScore": 0.5,
                "lastUpdated": "2025-08-10T12:00:00",
            }
        ]

        # Use a path that should cause permission error (depends on system)
        invalid_path = Path("/root/forbidden/results.json")

        with pytest.raises(OSError):  # Should raise OSError for permission/path issues
            write_results_json(results, invalid_path)


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple functions."""

    def test_full_workflow_simulation(self):
        """Test a complete workflow simulation with multiple files."""
        # Simulate multiple file analyses
        file_analyses = [
            {
                "filename": "sample1.fastq",
                "cage_id": "CAGE-01A",
                "srs_risk_score": 0.75,
                "risk_analysis_timestamp": "2025-08-10T12:00:00.000000",
            },
            {
                "filename": "sample2.fastq",
                "cage_id": "CAGE-02B",
                "srs_risk_score": 0.25,
                "risk_analysis_timestamp": "2025-08-10T12:01:00.000000",
            },
            {
                "filename": "invalid_sample.fastq",
                "cage_id": None,  # This should be filtered out
                "srs_risk_score": 0.50,
                "risk_analysis_timestamp": "2025-08-10T12:02:00.000000",
            },
        ]

        # Extract results (simulating the main script logic)
        results = []
        for analysis in file_analyses:
            extracted = extract_result_data(analysis)
            if extracted:
                results.append(extracted)

        # Should have only valid results
        assert len(results) == 2
        assert results[0]["cageId"] == "CAGE-01A"
        assert results[1]["cageId"] == "CAGE-02B"

        # Write and verify
        with tempfile.TemporaryDirectory() as temp_dir:
            results_file = Path(temp_dir) / "results.json"
            write_results_json(results, results_file)

            # Read back and verify format matches expected
            with open(results_file, encoding="utf-8") as f:
                final_data = json.load(f)

            assert len(final_data) == 2
            # Verify exact format required by issue #31
            for entry in final_data:
                assert "cageId" in entry
                assert "srsRiskScore" in entry
                assert "lastUpdated" in entry
                assert isinstance(entry["cageId"], str)
                assert isinstance(entry["srsRiskScore"], int | float)
                assert isinstance(entry["lastUpdated"], str)
