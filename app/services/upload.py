"""
Upload service for handling fastq file uploads.

This module provides functionality for validating and storing fastq files
according to the project's naming convention and storage requirements.
"""

from pathlib import Path
import re

from fastapi import HTTPException, UploadFile


class UploadService:
    """Service for handling fastq file uploads."""

    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the upload service with the specified directory."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

        # File naming pattern: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq
        self.filename_pattern = re.compile(
            r"^([A-Za-z0-9_-]+)_([A-Z0-9_-]+)_(\d{4}-\d{2}-\d{2})_([A-Za-z0-9_-]+)\.fastq$"
        )

    def validate_filename(self, filename: str) -> tuple[bool, str | None]:
        """
        Validate filename against the required naming convention.

        Args:
            filename: The filename to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename.endswith(".fastq"):
            return False, "File must have .fastq extension"

        if not self.filename_pattern.match(filename):
            return False, (
                "Filename must follow the pattern: "
                "PartnerID_CageID_YYYY-MM-DD_SampleID.fastq "
                "(e.g., Mowi_CAGE-04B_2025-08-15_S01.fastq)"
            )

        return True, None

    def validate_file_content(self, file: UploadFile) -> tuple[bool, str | None]:
        """
        Validate that the file appears to be a valid fastq file.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file.content_type not in ["text/plain", "application/octet-stream", None]:
            return False, "Invalid file type. Expected text/plain or fastq file."

        # For now, we'll do basic validation - fastq files should start with @
        # In a production system, you might want more thorough validation
        return True, None

    async def save_file(self, file: UploadFile) -> tuple[str, dict]:
        """
        Save the uploaded file to the upload directory.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (saved_filepath, metadata)

        Raises:
            HTTPException: If validation fails or file cannot be saved
        """
        # Validate filename
        is_valid_name, name_error = self.validate_filename(file.filename)
        if not is_valid_name:
            raise HTTPException(status_code=400, detail=name_error)

        # Validate file content
        is_valid_content, content_error = self.validate_file_content(file)
        if not is_valid_content:
            raise HTTPException(status_code=400, detail=content_error)

        # Extract metadata from filename
        match = self.filename_pattern.match(file.filename)
        metadata = {
            "partner_id": match.group(1),
            "cage_id": match.group(2),
            "sample_date": match.group(3),
            "sample_id": match.group(4),
            "original_filename": file.filename,
            "file_size": 0,
        }

        # Save the file
        file_path = self.upload_dir / file.filename

        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=409, detail=f"File {file.filename} already exists"
            )

        try:
            # Write file content
            content = await file.read()
            metadata["file_size"] = len(content)

            # Basic fastq format validation - should start with @
            if content and not content.decode(
                "utf-8", errors="ignore"
            ).strip().startswith("@"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid fastq file format. File should start with '@'",
                )

            with open(file_path, "wb") as f:
                f.write(content)

            return str(file_path), metadata

        except HTTPException:
            # Re-raise HTTP exceptions (validation errors)
            # Clean up partial file if save failed
            if file_path.exists():
                file_path.unlink()
            raise
        except Exception as e:
            # Clean up partial file if save failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500, detail=f"Failed to save file: {e!s}"
            ) from e

    def get_uploaded_files(self) -> list:
        """Get a list of all uploaded files with metadata."""
        files = []
        for file_path in self.upload_dir.glob("*.fastq"):
            if self.filename_pattern.match(file_path.name):
                match = self.filename_pattern.match(file_path.name)
                files.append(
                    {
                        "filename": file_path.name,
                        "partner_id": match.group(1),
                        "cage_id": match.group(2),
                        "sample_date": match.group(3),
                        "sample_id": match.group(4),
                        "file_size": file_path.stat().st_size,
                        "upload_time": file_path.stat().st_mtime,
                    }
                )
        return files
