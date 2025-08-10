"""
Unit tests for the analysis service.

This module tests the AnalysisService functionality including
fastq file discovery, file information retrieval, and error handling.
"""

import contextlib
import os
from pathlib import Path
import tempfile

import pytest

from app.services.analysis import AnalysisService


class TestAnalysisService:
    """Test cases for AnalysisService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def analysis_service(self, temp_dir):
        """Create an analysis service with a temporary directory."""
        return AnalysisService(upload_dir=temp_dir)

    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample fastq files for testing."""
        files = [
            "sample1.fastq",
            "sample2.fq",
            "sample3.fastq.gz",
            "sample4.fq.gz",
            "not_fastq.txt",  # This should be ignored
            "another.log",  # This should be ignored
        ]

        file_paths = []
        for filename in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text("@SEQ1\nACGT\n+\nHHHH\n")  # Basic fastq content
            file_paths.append(file_path)

        return file_paths

    def test_discover_fastq_files_empty_directory(self, analysis_service):
        """Test file discovery in empty directory."""
        files = analysis_service.discover_fastq_files()
        assert files == []

    def test_discover_fastq_files_with_fastq_files(
        self, analysis_service, sample_files
    ):
        """Test file discovery with various fastq file types."""
        files = analysis_service.discover_fastq_files()

        # Should find only the 4 fastq files, not the txt/log files
        assert len(files) == 4

        # Check that all found files are fastq files
        found_names = {f.name for f in files}
        expected_names = {
            "sample1.fastq",
            "sample2.fq",
            "sample3.fastq.gz",
            "sample4.fq.gz",
        }
        assert found_names == expected_names

    def test_discover_fastq_files_sorted_output(self, analysis_service, sample_files):
        """Test that file discovery returns sorted results."""
        files = analysis_service.discover_fastq_files()
        file_names = [f.name for f in files]

        # Should be sorted alphabetically
        assert file_names == sorted(file_names)

    def test_discover_fastq_files_nonexistent_directory(self):
        """Test file discovery with non-existent directory."""
        service = AnalysisService(upload_dir="/nonexistent/directory")

        with pytest.raises(FileNotFoundError) as exc_info:
            service.discover_fastq_files()

        assert "Upload directory does not exist" in str(exc_info.value)

    def test_discover_fastq_files_file_instead_of_directory(self, temp_dir):
        """Test file discovery when upload path is a file, not directory."""
        # Create a file where directory should be
        file_path = Path(temp_dir) / "not_a_directory.txt"
        file_path.write_text("content")

        service = AnalysisService(upload_dir=str(file_path))

        with pytest.raises(NotADirectoryError) as exc_info:
            service.discover_fastq_files()

        assert "Upload path is not a directory" in str(exc_info.value)

    def test_is_fastq_file_valid_extensions(self, analysis_service):
        """Test fastq file detection with valid extensions."""
        valid_files = [
            Path("test.fastq"),
            Path("test.fq"),
            Path("test.fastq.gz"),
            Path("test.fq.gz"),
            Path("TEST.FASTQ"),  # Case insensitive
            Path("TEST.FQ.GZ"),  # Case insensitive
        ]

        for file_path in valid_files:
            assert analysis_service._is_fastq_file(file_path), (  # noqa: SLF001
                f"{file_path.name} should be recognized as fastq"
            )

    def test_is_fastq_file_invalid_extensions(self, analysis_service):
        """Test fastq file detection with invalid extensions."""
        invalid_files = [
            Path("test.txt"),
            Path("test.log"),
            Path("test.json"),
            Path("test.fastq.bak"),  # Wrong extension after .fastq
            Path("test.gz"),  # Missing fastq part
            Path("fastq"),  # No extension
        ]

        for file_path in invalid_files:
            assert not analysis_service._is_fastq_file(file_path), (  # noqa: SLF001
                f"{file_path.name} should not be recognized as fastq"
            )

    def test_get_file_info_existing_file(self, analysis_service, temp_dir):
        """Test getting file information for existing file."""
        # Create a test file
        test_file = Path(temp_dir) / "test.fastq"
        content = "@SEQ1\nACGTACGT\n+\nHHHHHHHH\n"
        test_file.write_text(content)

        file_info = analysis_service.get_file_info(test_file)

        assert file_info["filename"] == "test.fastq"
        assert file_info["full_path"] == str(test_file.absolute())
        assert file_info["size_bytes"] == len(content)
        assert "modified_time" in file_info
        assert file_info["is_compressed"] is False

    def test_get_file_info_compressed_file(self, analysis_service, temp_dir):
        """Test getting file information for compressed file."""
        test_file = Path(temp_dir) / "test.fastq.gz"
        test_file.write_text("compressed content")

        file_info = analysis_service.get_file_info(test_file)

        assert file_info["filename"] == "test.fastq.gz"
        assert file_info["is_compressed"] is True

    def test_get_file_info_nonexistent_file(self, analysis_service, temp_dir):
        """Test getting file information for non-existent file."""
        nonexistent_file = Path(temp_dir) / "nonexistent.fastq"

        with pytest.raises(FileNotFoundError) as exc_info:
            analysis_service.get_file_info(nonexistent_file)

        assert "File does not exist" in str(exc_info.value)

    def test_get_all_files_info(self, analysis_service, sample_files):
        """Test getting information for all files in directory."""
        files_info = analysis_service.get_all_files_info()

        # Should get info for 4 fastq files
        assert len(files_info) == 4

        # Each info dict should have required fields
        for file_info in files_info:
            assert "filename" in file_info
            assert "full_path" in file_info
            assert "size_bytes" in file_info
            assert "modified_time" in file_info
            assert "is_compressed" in file_info

    def test_get_all_files_info_empty_directory(self, analysis_service):
        """Test getting file information from empty directory."""
        files_info = analysis_service.get_all_files_info()
        assert files_info == []

    def test_initialization_creates_logger_message(self, temp_dir, caplog):
        """Test that service initialization logs the upload directory."""
        with caplog.at_level("INFO"):
            AnalysisService(upload_dir=temp_dir)

        assert (
            f"Analysis service initialized with upload directory: {temp_dir}"
            in caplog.text
        )

    def test_discover_files_logs_results(self, analysis_service, sample_files, caplog):
        """Test that file discovery logs the number of files found."""
        with caplog.at_level("INFO"):
            analysis_service.discover_fastq_files()

        assert "Discovered 4 fastq files" in caplog.text

    def test_get_all_files_info_logs_results(
        self, analysis_service, sample_files, caplog
    ):
        """Test that get_all_files_info logs the results."""
        with caplog.at_level("INFO"):
            analysis_service.get_all_files_info()

        assert "Retrieved info for 4 fastq files" in caplog.text

    def test_permission_error_handling(self, analysis_service, temp_dir):
        """Test handling of permission errors when scanning directory."""
        # Create a directory with no read permissions (if possible)
        restricted_dir = Path(temp_dir) / "restricted"
        restricted_dir.mkdir()

        # Try to remove read permissions (may not work on all systems)
        try:
            os.chmod(restricted_dir, 0o000)
            service = AnalysisService(upload_dir=str(restricted_dir))

            with pytest.raises(PermissionError):
                service.discover_fastq_files()
        except (OSError, PermissionError):
            # Skip this test if we can't create permission restrictions
            pytest.skip("Cannot create permission restrictions on this system")
        finally:
            # Restore permissions for cleanup
            with contextlib.suppress(OSError, PermissionError):
                os.chmod(restricted_dir, 0o755)

    def test_get_file_info_with_valid_filename(self, analysis_service, temp_dir):
        """Test getting file info with valid filename that can be parsed."""
        # Create a file with valid filename
        test_file = Path(temp_dir) / "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        content = "@SEQ1\nACGT\n+\nHHHH\n"
        test_file.write_text(content)

        file_info = analysis_service.get_file_info(test_file)

        # Check basic file info
        assert file_info["filename"] == "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        assert file_info["size_bytes"] == len(content)
        assert file_info["is_compressed"] is False

        # Check parsed metadata
        assert file_info["filename_valid"] is True
        assert file_info["partner_id"] == "Mowi"
        assert file_info["cage_id"] == "CAGE-04B"
        assert file_info["sample_date"] == "2025-08-15"
        assert file_info["sample_id"] == "S01"
        assert file_info["parsed_date"] is not None
        assert "parse_error" not in file_info

    def test_get_file_info_with_invalid_filename(self, analysis_service, temp_dir):
        """Test getting file info with invalid filename that cannot be parsed."""
        # Create a file with invalid filename
        test_file = Path(temp_dir) / "invalid_filename.fastq"
        content = "@SEQ1\nACGT\n+\nHHHH\n"
        test_file.write_text(content)

        file_info = analysis_service.get_file_info(test_file)

        # Check basic file info
        assert file_info["filename"] == "invalid_filename.fastq"
        assert file_info["size_bytes"] == len(content)

        # Check parsed metadata failure
        assert file_info["filename_valid"] is False
        assert file_info["partner_id"] is None
        assert file_info["cage_id"] is None
        assert file_info["sample_date"] is None
        assert file_info["sample_id"] is None
        assert file_info["parsed_date"] is None
        assert "parse_error" in file_info

    def test_get_files_by_partner(self, analysis_service, temp_dir):
        """Test filtering files by partner ID."""
        # Create files for different partners
        files = [
            "Mowi_CAGE-01_2025-08-15_S01.fastq",
            "Mowi_CAGE-02_2025-08-15_S02.fastq",
            "Partner2_CAGE-01_2025-08-15_S01.fastq",
            "invalid_filename.fastq",
        ]

        for filename in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        mowi_files = analysis_service.get_files_by_partner("Mowi")

        assert len(mowi_files) == 2
        assert all(f["partner_id"] == "Mowi" for f in mowi_files)
        assert all(f["filename_valid"] for f in mowi_files)

    def test_get_files_by_cage(self, analysis_service, temp_dir):
        """Test filtering files by cage ID."""
        # Create files for different cages
        files = [
            "Mowi_CAGE-01_2025-08-15_S01.fastq",
            "Partner2_CAGE-01_2025-08-15_S02.fastq",
            "Mowi_CAGE-02_2025-08-15_S03.fastq",
            "invalid_filename.fastq",
        ]

        for filename in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        cage01_files = analysis_service.get_files_by_cage("CAGE-01")

        assert len(cage01_files) == 2
        assert all(f["cage_id"] == "CAGE-01" for f in cage01_files)
        assert all(f["filename_valid"] for f in cage01_files)

    def test_get_invalid_filenames(self, analysis_service, temp_dir):
        """Test getting files with invalid filenames."""
        # Create mix of valid and invalid files
        files = [
            "Mowi_CAGE-01_2025-08-15_S01.fastq",  # Valid
            "invalid_filename.fastq",  # Invalid
            "also_invalid.fastq",  # Invalid
            "Partner_CAGE-02_2025-08-15_S02.fastq",  # Valid
        ]

        for filename in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        invalid_files = analysis_service.get_invalid_filenames()

        assert len(invalid_files) == 2
        assert all(not f["filename_valid"] for f in invalid_files)
        invalid_names = {f["filename"] for f in invalid_files}
        assert invalid_names == {"invalid_filename.fastq", "also_invalid.fastq"}

    def test_validate_all_filenames(self, analysis_service, temp_dir):
        """Test validation summary of all filenames."""
        # Create mix of valid and invalid files
        files = [
            "Mowi_CAGE-01_2025-08-15_S01.fastq",  # Valid
            "Partner_CAGE-02_2025-08-15_S02.fastq",  # Valid
            "invalid_filename.fastq",  # Invalid
            "also_invalid.fastq",  # Invalid
        ]

        for filename in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        summary = analysis_service.validate_all_filenames()

        assert summary["total_files"] == 4
        assert summary["valid_files"] == 2
        assert summary["invalid_files"] == 2
        assert len(summary["invalid_file_details"]) == 2

        # Check invalid file details
        invalid_names = {
            detail["filename"] for detail in summary["invalid_file_details"]
        }
        assert invalid_names == {"invalid_filename.fastq", "also_invalid.fastq"}

        for detail in summary["invalid_file_details"]:
            assert "error" in detail
            assert detail["error"] != ""

    def test_filename_parser_integration_logging(
        self, analysis_service, temp_dir, caplog
    ):
        """Test that filename parsing integrates properly with logging."""
        # Test with valid filename
        valid_file = Path(temp_dir) / "Mowi_CAGE-01_2025-08-15_S01.fastq"
        valid_file.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        # Test with invalid filename
        invalid_file = Path(temp_dir) / "invalid_filename.fastq"
        invalid_file.write_text("@SEQ1\nACGT\n+\nHHHH\n")

        with caplog.at_level("DEBUG"):
            analysis_service.get_file_info(valid_file)

        assert "Successfully parsed metadata" in caplog.text

        with caplog.at_level("WARNING"):
            analysis_service.get_file_info(invalid_file)

        assert "Failed to parse filename" in caplog.text
