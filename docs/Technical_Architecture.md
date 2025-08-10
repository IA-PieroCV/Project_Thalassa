# Technical Architecture Document: Project Thalassa

_This document outlines the chosen tech stack and high-level architecture for the MVP, designed to test the core business hypothesis in 3-4 weeks._

---

## 1. Guiding Architectural Principles

_The core technical drivers derived from the project goals that influenced our decisions._

- **Extreme Speed to Market:** Every decision prioritizes the fastest path to a functional MVP to meet the 3-4 week development cycle. This overrides architectural purity.
- **Pragmatic Tooling & Minimal Complexity:** Choose the simplest tool that reliably accomplishes the job. The stack should have the absolute minimum number of moving parts.
- **Decoupled for the Future:** The initial architecture, while simple, consists of containerized components that do not prevent a future migration to more scalable, robust services post-validation.

---

## 2. Chosen Technology Stack

_The definitive list of technologies approved for the MVP._

| Category                          | Technology                 | Rationale                                                                                                                       |
| :-------------------------------- | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **Backend & Analytics**           | Python                     | The de-facto standard for the core data science and bioinformatic analysis required.                                            |
| **Web App (Dashboard & Uploads)** | FastAPI (Python)           | A single, lightweight application serves both the results dashboard and the file upload endpoint, minimizing complexity.        |
| **Deployment**                    | Docker on existing OCI VPS | Leverages existing, maintained infrastructure and team familiarity. The entire application runs as a single container.          |
| **Authentication**                | Shared Bearer Token        | Provides a simple but effective security layer for the MVP's web-facing endpoints without the complexity of a full user system. |

---

## 3. High-Level System Architecture

_A simplified description of how the major components and processes interact._

1.  **Data Upload (Manual):** The pilot partner navigates to a secure upload endpoint on our FastAPI application, authenticates with the shared token, and uploads the `fastq` files directly to the server.
2.  **File Storage:** The uploaded files are saved directly to the local filesystem of the **OCI VPS**.
3.  **Analysis Execution (Manual):** A Thalassa team member triggers the analysis function within the same application (or as a separate script) on the **OCI VPS**.
4.  **Data Processing:** The Analysis Service automatically discovers and scans uploaded `fastq` files from the local filesystem, performs the SRS risk analysis, and outputs the results to a simple `results.json` file, also on the local filesystem.
5.  **Dashboard Access:** The partner accesses the dashboard URL, authenticates with the same token, and the FastAPI app displays the results from the `results.json` file.

### 3.1 Analysis Service

The Analysis Service (`app/services/analysis.py`) provides the foundational file discovery and processing capabilities for the SRS risk assessment pipeline:

- **File Discovery:** Automatically scans the upload directory for fastq files with supported extensions (`.fastq`, `.fq`, `.fastq.gz`, `.fq.gz`)
- **Filename Parsing:** Integrates with the FilenameParser to extract structured metadata from filenames following the `PartnerID_CageID_YYYY-MM-DD_SampleID.fastq` convention
- **Metadata Extraction:** Retrieves both file system information (size, modification time, compression status) and parsed filename components (partner ID, cage ID, sample date, sample ID)
- **Filtering & Validation:** Provides methods to filter files by partner or cage, identify invalid filenames, and validate filename compliance
- **Error Handling:** Comprehensive error handling for directory access, file permissions, and invalid file types with graceful degradation for unparseable filenames
- **Logging Integration:** Full logging integration for monitoring and debugging file operations and parsing results

The service supports case-insensitive file extension matching, returns sorted results for consistent processing order, and maintains backward compatibility for files with invalid naming patterns.

### 3.2 Filename Parser

The Filename Parser (`app/services/filename_parser.py`) handles the extraction of structured metadata from fastq filenames:

- **Pattern Matching:** Uses regex-based parsing to extract components from the standardized filename format: `PartnerID_CageID_YYYY-MM-DD_SampleID.fastq`
- **Component Extraction:** Separates filenames into partner ID, cage ID, sample date, sample ID, and file extension
- **Date Validation:** Validates date components and converts them to datetime objects for further processing
- **Extension Support:** Recognizes all supported fastq extensions (`.fastq`, `.fq`, `.fastq.gz`, `.fq.gz`) with compression detection
- **Error Handling:** Provides detailed error messages for malformed filenames while maintaining system stability
- **Security Considerations:** Implements ReDoS-resistant regex patterns to prevent denial-of-service attacks

The parser is designed to be strict with the naming convention while providing helpful error messages for debugging filename issues.

---

## 4. Data Structure & Naming Convention

_Instead of a database, we will rely on a strict file-system-based structure for the MVP._

- **File Naming Convention:** All incoming data files must adhere to a strict naming scheme to provide necessary metadata.
  - **Format:** `PartnerID_CageID_YYYY-MM-DD_SampleID.fastq`
  - **Example:** `Mowi_CAGE-04B_2025-08-15_S01.fastq`
- **Results File:** The output of the analysis will be a single, overwritten file.
  - **File:** `results.json`
  - **Structure:** `[{ "cageId": "CAGE-04B", "srsRiskScore": 0.85, "lastUpdated": "2025-08-16T10:00:00Z" }]`

---

## 5. Key Decisions & Trade-offs Log

_A record of critical decisions made during the architectural dialogue._

- **Decision:** Chose the existing **OCI VPS** for deployment over a serverless platform like Google Cloud Run.
  - **Reason:** To leverage existing infrastructure that is already being maintained and with which the team is familiar. This is a pragmatic choice accepting the trade-off of manual server management in exchange for using a readily available asset.
- **Decision:** Chose a **self-hosted FastAPI endpoint** for file uploads over a cloud service like Google Cloud Storage.
  - **Reason:** To completely eliminate financial risk and the complexity of managing cloud billing. This choice was made accepting the trade-off of taking on direct responsibility for securing the public-facing upload endpoint.
- **Decision:** Explicitly chose **no database** for the MVP.
  - **Reason:** A database adds unnecessary complexity and development time. A simple `json` file combined with a strict file naming convention is sufficient to meet all requirements of the MVP scope and aligns with the principle of "Extreme Speed to Market."
