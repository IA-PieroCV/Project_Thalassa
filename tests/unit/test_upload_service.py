"""
Unit tests for the upload service.

This module tests the UploadService functionality including
filename validation, file content validation, and file saving operations.
"""

from pathlib import Path
import tempfile
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException, UploadFile
import pytest

from app.services.upload import UploadService


class TestUploadService:
    """Test cases for UploadService."""

    @pytest.fixture
    def upload_service(self):
        """Create an upload service with a temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = UploadService(upload_dir=temp_dir)
            yield service

    def test_validate_filename_valid(self, upload_service):
        """Test filename validation with valid filenames."""
        valid_filenames = [
            "Mowi_CAGE-04B_2025-08-15_S01.fastq",
            "Partner123_CAGE_001_2025-12-31_SAMPLE_A.fastq",
            "TEST-Partner_CAGE-99_2025-01-01_S999.fastq",
        ]

        for filename in valid_filenames:
            is_valid, error = upload_service.validate_filename(filename)
            assert is_valid, f"Expected {filename} to be valid, but got error: {error}"
            assert error is None

    def test_validate_filename_invalid_extension(self, upload_service):
        """Test filename validation with invalid file extensions."""
        invalid_filenames = [
            "Mowi_CAGE-04B_2025-08-15_S01.txt",
            "Mowi_CAGE-04B_2025-08-15_S01.fasta",
            "Mowi_CAGE-04B_2025-08-15_S01",
        ]

        for filename in invalid_filenames:
            is_valid, error = upload_service.validate_filename(filename)
            assert not is_valid
            assert "must have .fastq extension" in error

    def test_validate_filename_invalid_pattern(self, upload_service):
        """Test filename validation with invalid naming patterns."""
        invalid_filenames = [
            "invalid_filename.fastq",
            "Mowi_CAGE-04B_2025-08-15.fastq",  # Missing sample ID
            "Mowi_CAGE-04B_S01.fastq",  # Missing date
            "CAGE-04B_2025-08-15_S01.fastq",  # Missing partner ID
            "Mowi__2025-08-15_S01.fastq",  # Missing cage ID
            "Mowi_CAGE-04B_25-08-15_S01.fastq",  # Invalid date format
        ]

        for filename in invalid_filenames:
            is_valid, error = upload_service.validate_filename(filename)
            assert not is_valid
            assert "must follow the pattern" in error

    def test_validate_file_content_valid(self, upload_service):
        """Test file content validation with valid content types."""
        valid_files = [
            Mock(content_type="text/plain"),
            Mock(content_type="application/octet-stream"),
            Mock(content_type=None),
        ]

        for file in valid_files:
            is_valid, error = upload_service.validate_file_content(file)
            assert is_valid
            assert error is None

    def test_validate_file_content_invalid(self, upload_service):
        """Test file content validation with invalid content types."""
        invalid_files = [
            Mock(content_type="image/jpeg"),
            Mock(content_type="application/pdf"),
            Mock(content_type="text/html"),
        ]

        for file in invalid_files:
            is_valid, error = upload_service.validate_file_content(file)
            assert not is_valid
            assert "Invalid file type" in error

    @pytest.mark.asyncio
    async def test_save_file_success(self, upload_service):
        """Test successful file saving."""
        # Create a mock file with valid content
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"@SEQ_ID_1\nACGTACGT\n+\nHHHHHHHH\n"

        file_path, metadata = await upload_service.save_file(mock_file)

        # Verify file was saved
        assert Path(file_path).exists()
        assert Path(file_path).name == "Mowi_CAGE-04B_2025-08-15_S01.fastq"

        # Verify metadata
        assert metadata["partner_id"] == "Mowi"
        assert metadata["cage_id"] == "CAGE-04B"
        assert metadata["sample_date"] == "2025-08-15"
        assert metadata["sample_id"] == "S01"
        assert metadata["original_filename"] == "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        assert metadata["file_size"] > 0

    @pytest.mark.asyncio
    async def test_save_file_invalid_filename(self, upload_service):
        """Test file saving with invalid filename."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "invalid_filename.fastq"
        mock_file.content_type = "text/plain"

        with pytest.raises(HTTPException) as exc_info:
            await upload_service.save_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "must follow the pattern" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_save_file_invalid_content(self, upload_service):
        """Test file saving with invalid fastq content."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"This is not a valid fastq file"

        with pytest.raises(HTTPException) as exc_info:
            await upload_service.save_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "Invalid fastq file format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_save_file_already_exists(self, upload_service):
        """Test file saving when file already exists."""
        # First, save a file
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"@SEQ_ID_1\nACGTACGT\n+\nHHHHHHHH\n"

        await upload_service.save_file(mock_file)

        # Try to save the same file again
        mock_file.read.return_value = b"@SEQ_ID_1\nACGTACGT\n+\nHHHHHHHH\n"

        with pytest.raises(HTTPException) as exc_info:
            await upload_service.save_file(mock_file)

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail

    def test_get_uploaded_files_empty(self, upload_service):
        """Test getting uploaded files when directory is empty."""
        files = upload_service.get_uploaded_files()
        assert files == []

    def test_get_uploaded_files_with_files(self, upload_service):
        """Test getting uploaded files with existing files."""
        # Create a test file
        test_file = upload_service.upload_dir / "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        test_file.write_text("@SEQ_ID_1\nACGTACGT\n+\nHHHHHHHH\n")

        files = upload_service.get_uploaded_files()

        assert len(files) == 1
        assert files[0]["filename"] == "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        assert files[0]["partner_id"] == "Mowi"
        assert files[0]["cage_id"] == "CAGE-04B"
        assert files[0]["sample_date"] == "2025-08-15"
        assert files[0]["sample_id"] == "S01"
