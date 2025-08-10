"""
Integration tests for upload endpoints.

This module tests the upload API endpoints with real HTTP requests
and file uploads to ensure the complete upload workflow functions correctly.
"""

from pathlib import Path
import shutil
import tempfile

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.upload import UploadService


class TestUploadEndpoints:
    """Integration tests for upload API endpoints."""

    @pytest.fixture
    def temp_upload_dir(self):
        """Create a temporary upload directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after test
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def client(self, temp_upload_dir, monkeypatch):
        """Create a test client with isolated upload directory."""
        # Create a fresh upload service for each test
        from app.api import upload

        test_upload_service = UploadService(upload_dir=temp_upload_dir)
        monkeypatch.setattr(upload, "upload_service", test_upload_service)
        return TestClient(app)

    @pytest.fixture
    def temp_fastq_file(self):
        """Create a temporary fastq file for testing."""
        content = b"@SEQ_ID_1\nACGTACGTACGTACGT\n+\nHHHHHHHHHHHHHHHH\n@SEQ_ID_2\nTCGATCGATCGATCGA\n+\nIIIIIIIIIIIIIIII\n"

        with tempfile.NamedTemporaryFile(suffix=".fastq", delete=False) as f:
            f.write(content)
            f.flush()  # Ensure content is written to disk
            yield f.name

        # Clean up
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def invalid_fastq_file(self):
        """Create an invalid fastq file for testing."""
        content = b"This is not a valid fastq file content"

        with tempfile.NamedTemporaryFile(suffix=".fastq", delete=False) as f:
            f.write(content)
            f.flush()  # Ensure content is written to disk
            yield f.name

        # Clean up
        Path(f.name).unlink(missing_ok=True)

    def test_upload_health_check(self, client):
        """Test the upload health check endpoint."""
        response = client.get("/api/v1/upload/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "upload"
        assert "upload_directory" in data
        assert "directory_exists" in data

    def test_upload_fastq_file_success(self, client, temp_fastq_file):
        """Test successful fastq file upload."""
        # Read the file content
        with open(temp_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S01.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "File uploaded successfully"
        assert data["filename"] == "Mowi_CAGE-04B_2025-08-15_S01.fastq"
        assert "file_path" in data

        # Check metadata
        metadata = data["metadata"]
        assert metadata["partner_id"] == "Mowi"
        assert metadata["cage_id"] == "CAGE-04B"
        assert metadata["sample_date"] == "2025-08-15"
        assert metadata["sample_id"] == "S01"
        assert metadata["file_size"] > 0

    def test_upload_invalid_filename(self, client, temp_fastq_file):
        """Test upload with invalid filename."""
        with open(temp_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("invalid_filename.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "must follow the pattern" in data["detail"]

    def test_upload_invalid_extension(self, client, temp_fastq_file):
        """Test upload with invalid file extension."""
        with open(temp_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S01.txt", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "must have .fastq extension" in data["detail"]

    def test_upload_invalid_fastq_content(self, client, invalid_fastq_file):
        """Test upload with invalid fastq content."""
        with open(invalid_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S01.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid fastq file format" in data["detail"]

    def test_upload_duplicate_file(self, client, temp_fastq_file):
        """Test uploading the same file twice."""
        # First upload
        with open(temp_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S02.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 200

        # Second upload of the same file
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S02.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    def test_upload_no_file(self, client):
        """Test upload endpoint without providing a file."""
        response = client.post("/api/v1/upload")

        assert response.status_code == 422  # Validation error

    def test_list_uploaded_files_empty(self, client):
        """Test listing files when no files are uploaded."""
        response = client.get("/api/v1/upload/files")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total_count"] == 0

    def test_upload_and_list_files(self, client, temp_fastq_file):
        """Test uploading files and then listing them."""
        # Upload a file
        with open(temp_fastq_file, "rb") as f:
            content = f.read()
        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S03.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 200

        # List files
        response = client.get("/api/v1/upload/files")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) >= 1
        assert data["total_count"] >= 1

        # Check that our uploaded file is in the list
        uploaded_files = [
            f
            for f in data["files"]
            if f["filename"] == "Mowi_CAGE-04B_2025-08-15_S03.fastq"
        ]
        assert len(uploaded_files) == 1

        file_info = uploaded_files[0]
        assert file_info["partner_id"] == "Mowi"
        assert file_info["cage_id"] == "CAGE-04B"
        assert file_info["sample_date"] == "2025-08-15"
        assert file_info["sample_id"] == "S03"

    def test_upload_large_file(self, client):
        """Test uploading a larger fastq file."""
        # Create a larger fastq content
        sequences = []
        for i in range(100):
            sequences.append(f"@SEQ_ID_{i}")
            sequences.append("ACGTACGTACGTACGTACGTACGTACGTACGT")
            sequences.append("+")
            sequences.append("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")

        content = "\n".join(sequences).encode()

        files = {"file": ("Mowi_CAGE-04B_2025-08-15_S04.fastq", content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["file_size"] == len(content)
