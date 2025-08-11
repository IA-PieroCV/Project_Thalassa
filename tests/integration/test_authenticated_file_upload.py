"""
Integration test for authenticated file upload functionality.

This module provides comprehensive integration testing for the authenticated
file upload workflow as specified in Issue #27, validating the complete
end-to-end process from HTTP request to filesystem storage.
"""

from pathlib import Path
import shutil
import tempfile

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.upload import UploadService


class TestAuthenticatedFileUpload:
    """Integration test for authenticated file upload workflow per Issue #27."""

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
    def auth_headers(self, monkeypatch):
        """Create valid authentication headers for testing."""
        from app.services.auth import AuthService

        # Create a test auth service with the test token
        test_auth_service = AuthService(bearer_token="test-token-for-integration-tests")

        # Patch the global auth service instance
        monkeypatch.setattr("app.dependencies.auth.auth_service", test_auth_service)

        return {"Authorization": "Bearer test-token-for-integration-tests"}

    @pytest.fixture
    def sample_fastq_file(self):
        """Create a valid sample FASTQ file for testing."""
        # Create realistic FASTQ content with multiple sequences
        content = b"""@SEQ_ID_1
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
+
HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
@SEQ_ID_2
TCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@SEQ_ID_3
GGGAAATTTCCCGGGAAATTTCCCGGGAAATTTCCCGGGAAAT
+
JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ
"""

        with tempfile.NamedTemporaryFile(suffix=".fastq", delete=False) as f:
            f.write(content)
            f.flush()  # Ensure content is written to disk
            yield f.name

        # Clean up
        Path(f.name).unlink(missing_ok=True)

    def test_authenticated_file_upload_complete_workflow(
        self, client, sample_fastq_file, auth_headers, temp_upload_dir
    ):
        """
        Integration test for authenticated file upload complete workflow.

        This test addresses Issue #27 requirements:
        1. Uses HTTP client to POST sample file to upload endpoint
        2. Uses valid Bearer token authentication
        3. Asserts 200 OK response
        4. Verifies file was correctly saved to filesystem
        """
        # Prepare the file for upload
        with open(sample_fastq_file, "rb") as f:
            file_content = f.read()

        # Valid filename following project naming convention
        filename = "Mowi_CAGE-04B_2025-08-11_S01.fastq"
        files = {"file": (filename, file_content, "text/plain")}

        # POST request to upload endpoint with valid authentication
        response = client.post("/api/v1/upload", files=files, headers=auth_headers)

        # ASSERTION 1: Verify 200 OK response (Issue #27 requirement)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        # ASSERTION 2: Verify response structure and content
        response_data = response.json()
        assert response_data["message"] == "File uploaded successfully"
        assert response_data["filename"] == filename
        assert "file_path" in response_data
        assert "metadata" in response_data

        # ASSERTION 3: Verify file metadata extraction
        metadata = response_data["metadata"]
        assert metadata["partner_id"] == "Mowi"
        assert metadata["cage_id"] == "CAGE-04B"
        assert metadata["sample_date"] == "2025-08-11"
        assert metadata["sample_id"] == "S01"
        assert metadata["file_size"] == len(file_content)

        # ASSERTION 4: Verify file was saved to filesystem (Issue #27 requirement)
        expected_file_path = Path(temp_upload_dir) / filename
        assert expected_file_path.exists(), (
            f"File not found at expected path: {expected_file_path}"
        )

        # ASSERTION 5: Verify file content integrity
        with open(expected_file_path, "rb") as saved_file:
            saved_content = saved_file.read()
            assert saved_content == file_content, (
                "Saved file content does not match uploaded content"
            )

        # ASSERTION 6: Verify file permissions and readability
        assert expected_file_path.is_file(), "Saved path is not a regular file"
        assert expected_file_path.stat().st_size == len(file_content), (
            "File size mismatch"
        )

    def test_authenticated_upload_extension_validation(
        self, client, auth_headers, temp_upload_dir
    ):
        """Test that upload service properly validates file extensions."""
        # Create valid FASTQ content
        content = b"@SEQ_1\nACGTACGTACGTACGT\n+\nHHHHHHHHHHHHHHHH\n@SEQ_2\nTCGATCGATCGATCGA\n+\nIIIIIIIIIIIIIIII\n"

        # Test that .fastq.gz files are rejected by upload service (current system behavior)
        compressed_filename = "Mowi_CAGE-01A_2025-08-11_S02.fastq.gz"
        files = {"file": (compressed_filename, content, "application/gzip")}
        response = client.post("/api/v1/upload", files=files, headers=auth_headers)

        # Current upload service only accepts .fastq extension
        assert response.status_code == 400
        assert "File must have .fastq extension" in response.json()["detail"]

        # Test that invalid extensions are rejected
        invalid_filename = "Mowi_CAGE-01A_2025-08-11_S02.txt"
        files = {"file": (invalid_filename, content, "text/plain")}
        response = client.post("/api/v1/upload", files=files, headers=auth_headers)

        assert response.status_code == 400
        assert "File must have .fastq extension" in response.json()["detail"]

        # Verify no files were saved for failed validations
        compressed_path = Path(temp_upload_dir) / compressed_filename
        invalid_path = Path(temp_upload_dir) / invalid_filename
        assert not compressed_path.exists()
        assert not invalid_path.exists()

    def test_authenticated_upload_end_to_end_file_listing(
        self, client, sample_fastq_file, auth_headers, temp_upload_dir
    ):
        """Test complete upload workflow including file listing integration."""
        # Upload a file
        with open(sample_fastq_file, "rb") as f:
            file_content = f.read()

        filename = "Partner123_CAGE-TEST_2025-08-11_S99.fastq"
        files = {"file": (filename, file_content, "text/plain")}

        upload_response = client.post(
            "/api/v1/upload", files=files, headers=auth_headers
        )
        assert upload_response.status_code == 200

        # List files to verify integration
        list_response = client.get("/api/v1/upload/files", headers=auth_headers)
        assert list_response.status_code == 200

        list_data = list_response.json()
        assert list_data["total_count"] >= 1

        # Find our uploaded file in the list
        uploaded_files = [f for f in list_data["files"] if f["filename"] == filename]
        assert len(uploaded_files) == 1

        file_info = uploaded_files[0]
        assert file_info["partner_id"] == "Partner123"
        assert file_info["cage_id"] == "CAGE-TEST"
        assert file_info["sample_id"] == "S99"

    def test_authentication_failure_scenarios(
        self, client, sample_fastq_file, temp_upload_dir
    ):
        """Test that authentication failures are properly handled."""
        with open(sample_fastq_file, "rb") as f:
            file_content = f.read()

        filename = "Test_CAGE-01_2025-08-11_S01.fastq"
        files = {"file": (filename, file_content, "text/plain")}

        # Test without authentication
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 401
        assert "Authorization header is required" in response.json()["detail"]

        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/api/v1/upload", files=files, headers=invalid_headers)
        assert response.status_code == 401
        assert "Invalid bearer token" in response.json()["detail"]

        # Verify no file was saved in filesystem for failed uploads
        expected_file_path = Path(temp_upload_dir) / filename
        assert not expected_file_path.exists(), (
            "File should not be saved for failed authentication"
        )

    def test_upload_validation_with_authentication(
        self, client, auth_headers, temp_upload_dir
    ):
        """Test that file validation works correctly with authentication."""
        # Create invalid FASTQ content
        invalid_content = b"This is not a valid FASTQ file content"
        filename = "Valid_CAGE-01_2025-08-11_S01.fastq"
        files = {"file": (filename, invalid_content, "text/plain")}

        response = client.post("/api/v1/upload", files=files, headers=auth_headers)

        # Should be authenticated but fail validation
        assert response.status_code == 400
        assert "Invalid fastq file format" in response.json()["detail"]

        # Verify no file was saved for validation failure
        expected_file_path = Path(temp_upload_dir) / filename
        assert not expected_file_path.exists(), (
            "File should not be saved for validation failure"
        )
