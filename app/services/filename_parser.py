"""
Filename parser for extracting metadata from fastq files.

This module provides functionality for parsing fastq filenames based on the
convention: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq
"""

from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class FilenameParseError(Exception):
    """Exception raised when filename parsing fails."""


class FilenameParser:
    """Parser for extracting metadata from fastq filenames."""

    # Regex pattern for the filename convention: PartnerID_CageID_YYYY-MM-DD_SampleID.fastq
    # Use the date as an anchor - it's the only component with a specific format
    FILENAME_PATTERN = re.compile(
        r"^(?P<partner_id>[A-Za-z0-9\-]+)_"
        r"(?P<cage_id>[A-Za-z0-9\-_]+)_"
        r"(?P<date>\d{4}-\d{2}-\d{2})_"
        r"(?P<sample_id>[A-Za-z0-9\-_]+)"
        r"\.(?P<extension>fastq|fq|fastq\.gz|fq\.gz)$"
    )

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}

    def __init__(self):
        """Initialize the filename parser."""
        logger.info("Filename parser initialized")

    def parse_filename(self, filename: str) -> dict[str, Any]:
        """
        Parse a fastq filename to extract metadata components.

        Args:
            filename: The filename to parse

        Returns:
            Dictionary containing parsed metadata:
            - partner_id: The partner identifier
            - cage_id: The cage identifier
            - date: The sample date (YYYY-MM-DD format)
            - sample_id: The sample identifier
            - extension: The file extension
            - is_compressed: Whether the file is compressed
            - parsed_date: datetime object of the sample date

        Raises:
            FilenameParseError: If filename doesn't match expected pattern
        """
        if not filename:
            raise FilenameParseError("Filename cannot be empty")

        logger.debug(f"Parsing filename: {filename}")

        # Match against the pattern
        match = self.FILENAME_PATTERN.match(filename)

        if not match:
            error_msg = (
                f"Filename '{filename}' does not match expected pattern "
                f"'PartnerID_CageID_YYYY-MM-DD_SampleID.fastq'"
            )
            logger.error(error_msg)
            raise FilenameParseError(error_msg)

        # Extract components
        components = match.groupdict()

        # Validate and parse the date
        try:
            parsed_date = datetime.strptime(components["date"], "%Y-%m-%d")
        except ValueError as e:
            error_msg = (
                f"Invalid date format in filename '{filename}': {components['date']}"
            )
            logger.error(error_msg)
            raise FilenameParseError(error_msg) from e

        # Build metadata dictionary
        metadata = {
            "partner_id": components["partner_id"],
            "cage_id": components["cage_id"],
            "date": components["date"],
            "sample_id": components["sample_id"],
            "extension": components["extension"],
            "is_compressed": components["extension"].endswith(".gz"),
            "parsed_date": parsed_date,
            "original_filename": filename,
        }

        logger.debug(f"Successfully parsed filename: {metadata}")
        return metadata

    def parse_file_path(self, file_path: Path) -> dict[str, Any]:
        """
        Parse a file path to extract metadata from the filename.

        Args:
            file_path: Path object to the file

        Returns:
            Dictionary containing parsed metadata plus file path information

        Raises:
            FilenameParseError: If filename doesn't match expected pattern
        """
        metadata = self.parse_filename(file_path.name)

        # Add file path information
        metadata.update(
            {
                "full_path": str(file_path.absolute()),
                "directory": str(file_path.parent),
                "stem": file_path.stem,
            }
        )

        return metadata

    def is_valid_filename(self, filename: str) -> bool:
        """
        Check if a filename matches the expected pattern.

        Args:
            filename: The filename to validate

        Returns:
            True if filename matches pattern, False otherwise
        """
        try:
            self.parse_filename(filename)
            return True
        except FilenameParseError:
            return False

    def validate_filename(self, filename: str) -> tuple[bool, str | None]:
        """
        Validate a filename and return detailed error information.

        Args:
            filename: The filename to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if filename is valid
            - error_message: Error description if invalid, None if valid
        """
        try:
            self.parse_filename(filename)
            return True, None
        except FilenameParseError as e:
            return False, str(e)

    def extract_cage_id(self, filename: str) -> str:
        """
        Extract just the cage ID from a filename.

        Args:
            filename: The filename to parse

        Returns:
            The cage ID string

        Raises:
            FilenameParseError: If filename doesn't match expected pattern
        """
        metadata = self.parse_filename(filename)
        return metadata["cage_id"]

    def extract_partner_id(self, filename: str) -> str:
        """
        Extract just the partner ID from a filename.

        Args:
            filename: The filename to parse

        Returns:
            The partner ID string

        Raises:
            FilenameParseError: If filename doesn't match expected pattern
        """
        metadata = self.parse_filename(filename)
        return metadata["partner_id"]

    def get_supported_extensions(self) -> set[str]:
        """
        Get the set of supported file extensions.

        Returns:
            Set of supported file extensions
        """
        return self.SUPPORTED_EXTENSIONS.copy()
