"""
Pydantic schemas for upload endpoints.

This module defines the request and response models for file upload operations.
"""

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Metadata for an uploaded file."""

    partner_id: str = Field(
        ..., description="Partner identifier extracted from filename"
    )
    cage_id: str = Field(..., description="Cage identifier extracted from filename")
    sample_date: str = Field(..., description="Sample date in YYYY-MM-DD format")
    sample_id: str = Field(..., description="Sample identifier extracted from filename")
    original_filename: str = Field(
        ..., description="Original filename of the uploaded file"
    )
    file_size: int = Field(..., description="Size of the uploaded file in bytes")


class UploadResponse(BaseModel):
    """Response model for successful file upload."""

    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Name of the uploaded file")
    file_path: str = Field(..., description="Path where the file was saved")
    metadata: FileMetadata = Field(..., description="Extracted file metadata")


class UploadError(BaseModel):
    """Error response model for failed uploads."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    filename: str | None = Field(None, description="Filename that caused the error")


class UploadedFileInfo(BaseModel):
    """Information about an uploaded file."""

    filename: str = Field(..., description="Name of the uploaded file")
    partner_id: str = Field(
        ..., description="Partner identifier extracted from filename"
    )
    cage_id: str = Field(..., description="Cage identifier extracted from filename")
    sample_date: str = Field(..., description="Sample date in YYYY-MM-DD format")
    sample_id: str = Field(..., description="Sample identifier extracted from filename")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    upload_time: float = Field(..., description="Upload timestamp")


class FileListResponse(BaseModel):
    """Response model for listing uploaded files."""

    files: list[UploadedFileInfo] = Field(
        ..., description="List of uploaded files with metadata"
    )
    total_count: int = Field(..., description="Total number of files")
