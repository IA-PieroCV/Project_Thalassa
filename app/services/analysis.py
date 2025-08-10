"""
Analysis service for reading and processing fastq files.

This module provides functionality for discovering and reading fastq files
from the upload directory for SRS risk analysis processing.
"""

from datetime import datetime
import gzip
import hashlib
import logging
from pathlib import Path
import re

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

    def calculate_srs_risk_score(self, file_path: Path) -> float:
        """
        Calculate SRS risk score for a single fastq file.

        This method implements the core bioinformatics analysis for SRS risk assessment.
        The algorithm analyzes sequence data patterns to generate a risk score between 0.0 and 1.0.

        Args:
            file_path: Path to the fastq file to analyze

        Returns:
            Float between 0.0 (no risk) and 1.0 (critical risk)

        Raises:
            FileNotFoundError: If the file doesn't exist
            OSError: If the file cannot be read
            ValueError: If the file format is invalid
        """
        if not file_path.exists():
            error_msg = f"Cannot analyze non-existent file: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Starting SRS risk analysis for {file_path.name}")

        try:
            # Read and analyze fastq file content
            sequence_data = self._read_fastq_sequences(file_path)

            if not sequence_data:
                logger.warning(f"No valid sequences found in {file_path.name}")
                return 0.0

            # Core SRS risk analysis algorithm
            risk_score = self._analyze_srs_patterns(sequence_data)

            logger.info(
                f"SRS risk analysis complete for {file_path.name}: "
                f"risk_score={risk_score:.3f}"
            )

            return risk_score

        except Exception as e:
            error_msg = f"Error during SRS risk analysis for {file_path.name}: {e}"
            logger.error(error_msg)
            raise OSError(error_msg) from e

    def _read_fastq_sequences(self, file_path: Path) -> list[str]:
        """
        Read and parse sequences from a fastq file.

        Args:
            file_path: Path to the fastq file

        Returns:
            List of DNA sequences (without headers, quality scores)

        Raises:
            OSError: If file cannot be read
            ValueError: If file format is invalid
        """
        sequences = []

        try:
            # Handle both compressed and uncompressed files
            if file_path.name.endswith(".gz"):
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    return self._process_fastq_file(f)
            else:
                with open(file_path, encoding="utf-8") as f:
                    return self._process_fastq_file(f)
        except Exception as e:
            msg = f"Error reading FASTQ file {file_path}: {e!s}"
            logger.error(msg)
            raise ValueError(msg) from e

    def _process_fastq_file(self, f):
        """Process an open FASTQ file and return sequences."""
        sequences = []
        line_count = 0
        for line in f:
            line_count += 1
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Every 4th line starting from line 2 contains the sequence
            # Fastq format: @header, sequence, +, quality
            if line_count % 4 == 2:
                # Validate sequence contains only valid nucleotides
                if re.match(r"^[ACGTRYKMSWBDHVN]+$", line, re.IGNORECASE):
                    sequences.append(line.upper())
                else:
                    logger.debug(
                        f"Invalid sequence format at line {line_count}: {line[:50]}..."
                    )

        logger.debug(f"Extracted {len(sequences)} valid sequences")
        return sequences

    def _analyze_srs_patterns(self, sequences: list[str]) -> float:
        """
        Core SRS risk analysis algorithm.

        This method analyzes DNA sequences for patterns associated with SRS risk.
        The algorithm considers multiple factors including sequence diversity,
        GC content patterns, and specific pathogen-associated motifs.

        Args:
            sequences: List of DNA sequences to analyze

        Returns:
            Risk score between 0.0 and 1.0
        """
        if not sequences:
            return 0.0

        total_sequences = len(sequences)
        total_length = sum(len(seq) for seq in sequences)

        logger.debug(
            f"Analyzing {total_sequences} sequences, "
            f"total length: {total_length} nucleotides"
        )

        # Factor 1: Sequence diversity analysis
        diversity_score = self._calculate_sequence_diversity(sequences)

        # Factor 2: GC content analysis
        gc_score = self._calculate_gc_content_risk(sequences)

        # Factor 3: Pathogen-associated motif detection
        motif_score = self._detect_pathogen_motifs(sequences)

        # Factor 4: Quality indicators (length distribution, N-content)
        quality_score = self._calculate_quality_indicators(sequences)

        # Weighted combination of risk factors
        # Weights based on biological significance for SRS risk assessment
        risk_score = (
            0.3 * diversity_score
            + 0.25 * gc_score
            + 0.35 * motif_score
            + 0.1 * quality_score
        )

        # Ensure score is within valid range
        risk_score = max(0.0, min(1.0, risk_score))

        logger.debug(
            f"Risk factor breakdown: diversity={diversity_score:.3f}, "
            f"gc_content={gc_score:.3f}, motifs={motif_score:.3f}, "
            f"quality={quality_score:.3f}, final={risk_score:.3f}"
        )

        return risk_score

    def _calculate_sequence_diversity(self, sequences: list[str]) -> float:
        """Calculate sequence diversity as a risk indicator."""
        if len(sequences) < 2:
            return 0.0

        # Use sequence hashing to measure diversity
        unique_hashes = set()
        for seq in sequences[:1000]:  # Sample first 1000 sequences for performance
            seq_hash = hashlib.md5(seq.encode()).hexdigest()[:8]
            unique_hashes.add(seq_hash)

        diversity_ratio = len(unique_hashes) / min(len(sequences), 1000)

        # Lower diversity (more repetitive sequences) indicates higher risk
        # Convert to risk score: high diversity = low risk
        return max(0.0, 1.0 - diversity_ratio)

    def _calculate_gc_content_risk(self, sequences: list[str]) -> float:
        """Calculate GC content patterns as risk indicator."""
        gc_contents = []

        for seq in sequences[:500]:  # Sample for performance
            gc_count = seq.count("G") + seq.count("C")
            gc_content = gc_count / len(seq) if len(seq) > 0 else 0.0
            gc_contents.append(gc_content)

        if not gc_contents:
            return 0.0

        avg_gc = sum(gc_contents) / len(gc_contents)

        # Pathogen-associated GC content patterns
        # Extreme GC content (very high or very low) can indicate pathogen presence
        if avg_gc < 0.3 or avg_gc > 0.7:
            return min(1.0, abs(avg_gc - 0.5) * 2.0)

        return 0.0

    def _detect_pathogen_motifs(self, sequences: list[str]) -> float:
        """Detect pathogen-associated sequence motifs."""
        # Known pathogen-associated motifs (simplified for MVP)
        pathogen_motifs = [
            r"ATGCGT.{10,20}CGTATG",  # Example pathogen signature
            r"GGCTAG.{5,15}CTAGGC",  # Another pathogen pattern
            r"TTTAAA.{8,12}AAATTT",  # Virulence factor pattern
        ]

        total_motif_matches = 0
        total_sequences_checked = min(len(sequences), 200)

        for seq in sequences[:total_sequences_checked]:
            for motif_pattern in pathogen_motifs:
                matches = re.findall(motif_pattern, seq, re.IGNORECASE)
                total_motif_matches += len(matches)

        if total_sequences_checked == 0:
            return 0.0

        # Calculate motif density as risk indicator
        motif_density = total_motif_matches / total_sequences_checked

        # Convert motif density to risk score (0-1 range)
        return min(1.0, motif_density * 10.0)

    def _calculate_quality_indicators(self, sequences: list[str]) -> float:
        """Calculate sequence quality indicators affecting risk assessment."""
        if not sequences:
            return 0.0

        # Check for high N-content (ambiguous nucleotides)
        n_content_scores = []
        length_variations = []

        for seq in sequences[:100]:  # Sample for performance
            n_content = seq.count("N") / len(seq) if len(seq) > 0 else 0.0
            n_content_scores.append(n_content)
            length_variations.append(len(seq))

        avg_n_content = (
            sum(n_content_scores) / len(n_content_scores) if n_content_scores else 0.0
        )

        # High N-content indicates poor quality, which affects risk assessment reliability
        return min(1.0, avg_n_content * 5.0)

    def analyze_file(self, file_path: Path) -> dict:
        """
        Perform comprehensive analysis of a fastq file including SRS risk assessment.

        This method combines file metadata extraction with SRS risk analysis
        to provide complete file analysis results.

        Args:
            file_path: Path to the fastq file to analyze

        Returns:
            Dictionary containing file metadata and risk analysis results

        Raises:
            FileNotFoundError: If the file doesn't exist
            OSError: If the file cannot be processed
        """
        logger.info(f"Starting comprehensive analysis for {file_path.name}")

        # Get basic file information and metadata
        file_info = self.get_file_info(file_path)

        # Add SRS risk analysis if file has valid metadata
        try:
            risk_score = self.calculate_srs_risk_score(file_path)
            file_info.update(
                {
                    "srs_risk_score": risk_score,
                    "risk_analysis_timestamp": datetime.now().isoformat(),
                    "risk_level": self._categorize_risk_level(risk_score),
                }
            )
            logger.info(
                f"Complete analysis finished for {file_path.name}: "
                f"risk_score={risk_score:.3f}"
            )
        except Exception as e:
            logger.error(f"Risk analysis failed for {file_path.name}: {e}")
            file_info.update(
                {
                    "srs_risk_score": None,
                    "risk_analysis_timestamp": datetime.now().isoformat(),
                    "risk_level": "analysis_failed",
                    "risk_analysis_error": str(e),
                }
            )

        return file_info

    def _categorize_risk_level(self, risk_score: float) -> str:
        """
        Categorize numerical risk score into risk level categories.

        Args:
            risk_score: Risk score between 0.0 and 1.0

        Returns:
            Risk level category string
        """
        if risk_score >= 0.8:
            return "critical"
        if risk_score >= 0.6:
            return "high"
        if risk_score >= 0.4:
            return "medium"
        return "low"
