"""
Upload API endpoints for fastq file handling.

This module provides REST API endpoints for uploading and managing
fastq files according to the project requirements.
"""

from fastapi import APIRouter, HTTPException, UploadFile

from ..schemas.upload import FileListResponse, UploadResponse
from ..services.upload import UploadService

router = APIRouter(prefix="/api/v1", tags=["upload"])

# Initialize upload service
upload_service = UploadService()


@router.post("/upload", response_model=UploadResponse)
async def upload_fastq_file(file: UploadFile):
    """
    Upload a fastq file to the server.

    The file must follow the naming convention:
    PartnerID_CageID_YYYY-MM-DD_SampleID.fastq

    Example: Mowi_CAGE-04B_2025-08-15_S01.fastq
    """
    try:
        file_path, metadata = await upload_service.save_file(file)

        return UploadResponse(
            message="File uploaded successfully",
            filename=file.filename or "unknown",
            file_path=file_path,
            metadata=metadata,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Unexpected error during file upload: {e!s}"
        ) from e


@router.get("/upload/files", response_model=FileListResponse)
async def list_uploaded_files():
    """
    Get a list of all uploaded fastq files with their metadata.
    """
    try:
        files = upload_service.get_uploaded_files()
        return FileListResponse(files=files, total_count=len(files))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving file list: {e!s}"
        ) from e


@router.get("/upload/health")
async def upload_health_check():
    """Health check endpoint for upload service."""
    return {
        "status": "healthy",
        "service": "upload",
        "upload_directory": str(upload_service.upload_dir),
        "directory_exists": upload_service.upload_dir.exists(),
    }
