"""
Analysis service for reading and processing fastq files.

This module provides functionality for discovering and reading fastq files
from the upload directory for SRS risk analysis processing.
"""

import logging
from pathlib import Path

from .filename_parser import FilenameParseError, FilenameParser

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for analyzing fastq files for SRS risk assessment."""

    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialize the analysis service.

        Args:
            upload_dir: Directory containing uploaded fastq files
        """
        self.upload_dir = Path(upload_dir)
        self.supported_extensions = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}
        self.filename_parser = FilenameParser()

        logger.info(
            f"Analysis service initialized with upload directory: {self.upload_dir}"
        )

    def discover_fastq_files(self) -> list[Path]:
        """
        Scan the upload directory for fastq files.

        Returns:
            List of Path objects for discovered fastq files

        Raises:
            FileNotFoundError: If upload directory doesn't exist
        """
        if not self.upload_dir.exists():
            error_msg = f"Upload directory does not exist: {self.upload_dir}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        if not self.upload_dir.is_dir():
            error_msg = f"Upload path is not a directory: {self.upload_dir}"
            logger.error(error_msg)
            raise NotADirectoryError(error_msg)

        fastq_files = []

        try:
            # Scan directory for files with supported extensions
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file() and self._is_fastq_file(file_path):
                    fastq_files.append(file_path)
                    logger.debug(f"Found fastq file: {file_path.name}")

            logger.info(
                f"Discovered {len(fastq_files)} fastq files in {self.upload_dir}"
            )

        except PermissionError as e:
            error_msg = (
                f"Permission denied accessing upload directory: {self.upload_dir}"
            )
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"OS error scanning directory {self.upload_dir}: {e}"
            logger.error(error_msg)
            raise OSError(error_msg) from e

        return sorted(fastq_files)  # Return sorted for consistent ordering

    def _is_fastq_file(self, file_path: Path) -> bool:
        """
        Check if a file is a supported fastq file based on extension.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file has a supported fastq extension
        """
        # Check all possible fastq extensions
        file_name = file_path.name.lower()

        return any(file_name.endswith(ext.lower()) for ext in self.supported_extensions)

    def get_file_info(self, file_path: Path) -> dict:
        """
        Get metadata information about a fastq file.

        Args:
            file_path: Path to the fastq file

        Returns:
            Dictionary containing file metadata including parsed filename components
        """
        if not file_path.exists():
            error_msg = f"File does not exist: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            stat = file_path.stat()

            # Base file information
            file_info = {
                "filename": file_path.name,
                "full_path": str(file_path.absolute()),
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "is_compressed": file_path.name.lower().endswith(".gz"),
            }

            # Try to parse filename for additional metadata
            try:
                parsed_metadata = self.filename_parser.parse_file_path(file_path)
                file_info.update(
                    {
                        "partner_id": parsed_metadata["partner_id"],
                        "cage_id": parsed_metadata["cage_id"],
                        "sample_date": parsed_metadata["date"],
                        "sample_id": parsed_metadata["sample_id"],
                        "parsed_date": parsed_metadata["parsed_date"],
                        "filename_valid": True,
                    }
                )
                logger.debug(f"Successfully parsed metadata for {file_path.name}")
            except FilenameParseError as e:
                logger.warning(f"Failed to parse filename {file_path.name}: {e}")
                file_info.update(
                    {
                        "partner_id": None,
                        "cage_id": None,
                        "sample_date": None,
                        "sample_id": None,
                        "parsed_date": None,
                        "filename_valid": False,
                        "parse_error": str(e),
                    }
                )

            return file_info

        except OSError as e:
            error_msg = f"Error getting file info for {file_path}: {e}"
            logger.error(error_msg)
            raise OSError(error_msg) from e

    def get_all_files_info(self) -> list[dict]:
        """
        Get information about all fastq files in the upload directory.

        Returns:
            List of dictionaries containing file metadata
        """
        fastq_files = self.discover_fastq_files()
        files_info = []

        for file_path in fastq_files:
            try:
                file_info = self.get_file_info(file_path)
                files_info.append(file_info)
            except (FileNotFoundError, OSError) as e:
                logger.warning(f"Skipping file due to error: {e}")
                continue

        logger.info(f"Retrieved info for {len(files_info)} fastq files")
        return files_info

    def get_files_by_partner(self, partner_id: str) -> list[dict]:
        """
        Get all files for a specific partner.

        Args:
            partner_id: The partner identifier to filter by

        Returns:
            List of file info dictionaries for the specified partner
        """
        all_files = self.get_all_files_info()
        partner_files = [
            file_info
            for file_info in all_files
            if file_info.get("filename_valid")
            and file_info.get("partner_id") == partner_id
        ]

        logger.info(f"Found {len(partner_files)} files for partner '{partner_id}'")
        return partner_files

    def get_files_by_cage(self, cage_id: str) -> list[dict]:
        """
        Get all files for a specific cage.

        Args:
            cage_id: The cage identifier to filter by

        Returns:
            List of file info dictionaries for the specified cage
        """
        all_files = self.get_all_files_info()
        cage_files = [
            file_info
            for file_info in all_files
            if file_info.get("filename_valid") and file_info.get("cage_id") == cage_id
        ]

        logger.info(f"Found {len(cage_files)} files for cage '{cage_id}'")
        return cage_files

    def get_invalid_filenames(self) -> list[dict]:
        """
        Get all files with invalid filenames that couldn't be parsed.

        Returns:
            List of file info dictionaries for files with invalid names
        """
        all_files = self.get_all_files_info()
        invalid_files = [
            file_info
            for file_info in all_files
            if not file_info.get("filename_valid", False)
        ]

        logger.info(f"Found {len(invalid_files)} files with invalid filenames")
        return invalid_files

    def validate_all_filenames(self) -> dict:
        """
        Validate all fastq filenames in the upload directory.

        Returns:
            Dictionary with validation summary:
            - total_files: Total number of fastq files found
            - valid_files: Number of files with valid names
            - invalid_files: Number of files with invalid names
            - invalid_file_details: List of invalid files with error messages
        """
        all_files = self.get_all_files_info()

        valid_files = [f for f in all_files if f.get("filename_valid", False)]
        invalid_files = [f for f in all_files if not f.get("filename_valid", False)]

        summary = {
            "total_files": len(all_files),
            "valid_files": len(valid_files),
            "invalid_files": len(invalid_files),
            "invalid_file_details": [
                {
                    "filename": f["filename"],
                    "error": f.get("parse_error", "Unknown parsing error"),
                }
                for f in invalid_files
            ],
        }

        logger.info(
            f"Validation summary: {summary['valid_files']}/{summary['total_files']} "
            f"files have valid filenames"
        )

        return summary
