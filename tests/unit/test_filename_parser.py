"""
Unit tests for the filename parser.

This module tests the FilenameParser functionality including
filename parsing, metadata extraction, and error handling.
"""

from datetime import datetime
from pathlib import Path
import tempfile

import pytest

from app.services.filename_parser import FilenameParseError, FilenameParser


class TestFilenameParser:
    """Test cases for FilenameParser."""

    @pytest.fixture
    def parser(self):
        """Create a filename parser instance."""
        return FilenameParser()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_parse_valid_filename_basic(self, parser):
        """Test parsing a basic valid filename."""
        filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"

        result = parser.parse_filename(filename)

        assert result["partner_id"] == "Mowi"
        assert result["cage_id"] == "CAGE-04B"
        assert result["date"] == "2025-08-15"
        assert result["sample_id"] == "S01"
        assert result["extension"] == "fastq"
        assert result["is_compressed"] is False
        assert result["original_filename"] == filename
        assert isinstance(result["parsed_date"], datetime)
        assert result["parsed_date"] == datetime(2025, 8, 15)

    def test_parse_valid_filename_variations(self, parser):
        """Test parsing various valid filename formats."""
        test_cases = [
            {
                "filename": "Partner123_CAGE_001_2025-12-31_SAMPLE_A.fq",
                "expected": {
                    "partner_id": "Partner123",
                    "cage_id": "CAGE_001",
                    "date": "2025-12-31",
                    "sample_id": "SAMPLE_A",
                    "extension": "fq",
                    "is_compressed": False,
                },
            },
            {
                "filename": "TEST-Partner_CAGE-99_2025-01-01_S999.fastq.gz",
                "expected": {
                    "partner_id": "TEST-Partner",
                    "cage_id": "CAGE-99",
                    "date": "2025-01-01",
                    "sample_id": "S999",
                    "extension": "fastq.gz",
                    "is_compressed": True,
                },
            },
            {
                "filename": "Aqua_Farm_C1_2024-06-15_Sample01.fq.gz",
                "expected": {
                    "partner_id": "Aqua",
                    "cage_id": "Farm_C1",
                    "date": "2024-06-15",
                    "sample_id": "Sample01",
                    "extension": "fq.gz",
                    "is_compressed": True,
                },
            },
        ]

        for case in test_cases:
            result = parser.parse_filename(case["filename"])
            expected = case["expected"]

            assert result["partner_id"] == expected["partner_id"]
            assert result["cage_id"] == expected["cage_id"]
            assert result["date"] == expected["date"]
            assert result["sample_id"] == expected["sample_id"]
            assert result["extension"] == expected["extension"]
            assert result["is_compressed"] == expected["is_compressed"]

    def test_parse_invalid_filenames(self, parser):
        """Test parsing invalid filenames raises appropriate errors."""
        invalid_filenames = [
            "",  # Empty filename
            "invalid_filename.fastq",  # Too few components
            "Mowi_CAGE-04B_2025-08-15.fastq",  # Missing sample ID
            "Mowi_CAGE-04B_S01.fastq",  # Missing date
            "CAGE-04B_2025-08-15_S01.fastq",  # Missing partner ID
            "Mowi__2025-08-15_S01.fastq",  # Empty cage ID
            "Mowi_CAGE-04B_25-08-15_S01.fastq",  # Invalid date format
            "Mowi_CAGE-04B_2025-13-15_S01.fastq",  # Invalid month
            "Mowi_CAGE-04B_2025-08-32_S01.fastq",  # Invalid day
            "Mowi_CAGE-04B_2025-08-15_S01.txt",  # Invalid extension
            "Mowi_CAGE-04B_2025-08-15_S01.fastq.bak",  # Invalid extension
        ]

        for filename in invalid_filenames:
            with pytest.raises(FilenameParseError):
                parser.parse_filename(filename)

    def test_parse_file_path(self, parser, temp_dir):
        """Test parsing a file path object."""
        filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        file_path = Path(temp_dir) / filename
        file_path.write_text("test content")  # Create the file

        result = parser.parse_file_path(file_path)

        # Should have all the filename parsing results
        assert result["partner_id"] == "Mowi"
        assert result["cage_id"] == "CAGE-04B"
        assert result["date"] == "2025-08-15"
        assert result["sample_id"] == "S01"

        # Plus file path information
        assert result["full_path"] == str(file_path.absolute())
        assert result["directory"] == str(file_path.parent)
        assert result["stem"] == "Mowi_CAGE-04B_2025-08-15_S01"

    def test_is_valid_filename(self, parser):
        """Test filename validation without exceptions."""
        valid_filenames = [
            "Mowi_CAGE-04B_2025-08-15_S01.fastq",
            "Partner_C1_2024-01-01_Sample.fq",
            "Test_Cage_2025-12-31_S999.fastq.gz",
        ]

        invalid_filenames = [
            "invalid_filename.fastq",
            "Mowi_CAGE-04B_2025-08-15.fastq",
            "Mowi_CAGE-04B_25-08-15_S01.fastq",
        ]

        for filename in valid_filenames:
            assert parser.is_valid_filename(filename) is True

        for filename in invalid_filenames:
            assert parser.is_valid_filename(filename) is False

    def test_validate_filename(self, parser):
        """Test filename validation with error details."""
        valid_filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        is_valid, error = parser.validate_filename(valid_filename)

        assert is_valid is True
        assert error is None

        invalid_filename = "invalid_filename.fastq"
        is_valid, error = parser.validate_filename(invalid_filename)

        assert is_valid is False
        assert error is not None
        assert "does not match expected pattern" in error

    def test_extract_cage_id(self, parser):
        """Test extracting just the cage ID."""
        filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        cage_id = parser.extract_cage_id(filename)

        assert cage_id == "CAGE-04B"

        # Test with invalid filename
        with pytest.raises(FilenameParseError):
            parser.extract_cage_id("invalid_filename.fastq")

    def test_extract_partner_id(self, parser):
        """Test extracting just the partner ID."""
        filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        partner_id = parser.extract_partner_id(filename)

        assert partner_id == "Mowi"

        # Test with invalid filename
        with pytest.raises(FilenameParseError):
            parser.extract_partner_id("invalid_filename.fastq")

    def test_get_supported_extensions(self, parser):
        """Test getting supported extensions."""
        extensions = parser.get_supported_extensions()

        expected_extensions = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}
        assert extensions == expected_extensions

        # Make sure it returns a copy (not the original)
        extensions.add(".test")
        assert ".test" not in parser.get_supported_extensions()

    def test_complex_partner_names(self, parser):
        """Test parsing with complex partner names using hyphens (following convention)."""
        test_cases = [
            "Marine-Harvest_CAGE-01_2025-08-15_S01.fastq",
            "AquaCorp123_CAGE-A1_2025-08-15_Sample-01.fastq",
            "Fish-Farm-Co_CAGE-999_2025-08-15_S-001.fastq",
        ]

        expected_partners = ["Marine-Harvest", "AquaCorp123", "Fish-Farm-Co"]
        expected_cages = ["CAGE-01", "CAGE-A1", "CAGE-999"]
        expected_samples = ["S01", "Sample-01", "S-001"]

        for i, filename in enumerate(test_cases):
            result = parser.parse_filename(filename)
            assert result["partner_id"] == expected_partners[i]
            assert result["cage_id"] == expected_cages[i]
            assert result["sample_id"] == expected_samples[i]

    def test_date_edge_cases(self, parser):
        """Test parsing with various date formats and edge cases."""
        # Valid dates
        valid_dates = [
            "2024-01-01",  # New Year's Day
            "2024-02-29",  # Leap year
            "2024-12-31",  # Last day of year
        ]

        for date_str in valid_dates:
            filename = f"Partner_Cage_{date_str}_Sample.fastq"
            result = parser.parse_filename(filename)
            assert result["date"] == date_str

        # Invalid dates
        invalid_dates = [
            "2023-02-29",  # Not a leap year
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day for February
            "24-12-31",  # Wrong year format
            "2024-1-1",  # Wrong format (missing zeros)
        ]

        for date_str in invalid_dates:
            filename = f"Partner_Cage_{date_str}_Sample.fastq"
            with pytest.raises(FilenameParseError):
                parser.parse_filename(filename)

    def test_initialization_logging(self, caplog):
        """Test that parser initialization logs correctly."""
        with caplog.at_level("INFO"):
            FilenameParser()

        assert "Filename parser initialized" in caplog.text

    def test_parse_logging(self, parser, caplog):
        """Test that parsing operations log correctly."""
        filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"

        with caplog.at_level("DEBUG"):
            parser.parse_filename(filename)

        assert f"Parsing filename: {filename}" in caplog.text
        assert "Successfully parsed filename" in caplog.text

    def test_parse_error_logging(self, parser, caplog):
        """Test that parsing errors log correctly."""
        invalid_filename = "invalid_filename.fastq"

        with caplog.at_level("ERROR"), pytest.raises(FilenameParseError):
            parser.parse_filename(invalid_filename)

        assert "does not match expected pattern" in caplog.text

    def test_case_sensitivity(self, parser):
        """Test that parsing is case-sensitive for components but not extensions."""
        # Components should be case-sensitive
        filename1 = "MOWI_CAGE-04B_2025-08-15_S01.fastq"
        result1 = parser.parse_filename(filename1)
        assert result1["partner_id"] == "MOWI"  # Preserves case

        filename2 = "mowi_cage-04b_2025-08-15_s01.fastq"
        result2 = parser.parse_filename(filename2)
        assert result2["partner_id"] == "mowi"  # Preserves case
        assert result2["cage_id"] == "cage-04b"  # Preserves case

    def test_regex_security(self, parser):
        """Test that the regex doesn't have ReDoS vulnerabilities."""
        # Test with potentially problematic input
        problematic_inputs = [
            "a" * 1000 + "_" + "b" * 1000 + "_2025-08-15_S01.fastq",
            "Partner_" + "C" * 1000 + "_2025-08-15_S01.fastq",
            "Partner_Cage_2025-08-15_" + "S" * 1000 + ".fastq",
        ]

        for filename in problematic_inputs:
            # Should either parse successfully or fail quickly, not hang
            try:
                result = parser.parse_filename(filename)
                # If it parses, verify the components
                assert len(result["partner_id"]) > 0
                assert len(result["cage_id"]) > 0
                assert len(result["sample_id"]) > 0
            except FilenameParseError:
                # It's okay if it fails to parse, as long as it fails quickly
                pass
