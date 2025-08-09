# Technical Architecture Document: Project Thalassa
*This document outlines the chosen tech stack and high-level architecture for the MVP, designed to test the core business hypothesis in 3-4 weeks.*

---

## 1. Guiding Architectural Principles
*The core technical drivers derived from the project goals that influenced our decisions.*

- **Extreme Speed to Market:** Every decision prioritizes the fastest path to a functional MVP to meet the 3-4 week development cycle. This overrides architectural purity.
- **Pragmatic Tooling:** Choose the simplest tool that reliably accomplishes the job, avoiding unnecessary complexity (e.g., no database, no complex frontend framework).
- **Decoupled for the Future:** The initial architecture, while simple, consists of containerized components that do not prevent a future migration to more scalable, robust services post-validation.

---

## 2. Chosen Technology Stack
*The definitive list of technologies approved for the MVP.*

| Category | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend & Analytics** | Python | The de-facto standard for the core data science and bioinformatic analysis required. |
| **Web Dashboard** | FastAPI (Python) | A lightweight framework to serve a single, password-protected HTML page without the overhead of a separate frontend stack. |
| **Data Ingestion** | Google Cloud Storage | Provides a robust, secure, and programmatically simple upload target that meets the $0 cost goal via its free tier. |
| **Deployment** | Docker on existing OCI VPS | Leverages existing, maintained infrastructure and team familiarity. |
| **Authentication** | Shared Bearer Token | Provides a simple but effective security layer for the MVP's single dashboard without the complexity of a full user system. |

---

## 3. High-Level System Architecture
*A simplified description of how the major components and processes interact.*

1.  **Data Upload (Manual):** The pilot partner uploads `fastq` files to a dedicated **Google Cloud Storage** bucket using a secure link.
2.  **Analysis Execution (Manual):** A Thalassa team member triggers a **Docker container** running on the **OCI VPS**.
3.  **Data Processing:** The Python script within the container securely downloads the files from Google Cloud Storage, performs the SRS risk analysis, and outputs the results to a simple `results.json` file on the VPS's local filesystem.
4.  **Dashboard Access:** The partner accesses a URL pointing to the FastAPI application running in a separate container on the same VPS. They must provide the shared Bearer Token to authenticate.
5.  **Result Display:** The FastAPI application reads the `results.json` file and renders the risk scores into a simple, static HTML page for the partner.

---

## 4. Data Structure & Naming Convention
*Instead of a database, we will rely on a strict file-system-based structure for the MVP.*

- **File Naming Convention:** All incoming data files must adhere to a strict naming scheme to provide necessary metadata.
    - **Format:** `PartnerID_CageID_YYYY-MM-DD_SampleID.fastq`
    - **Example:** `Mowi_CAGE-04B_2025-08-15_S01.fastq`
- **Results File:** The output of the analysis will be a single, overwritten file.
    - **File:** `results.json`
    - **Structure:** `[{ "cageId": "CAGE-04B", "srsRiskScore": 0.85, "lastUpdated": "2025-08-16T10:00:00Z" }]`

---

## 5. Key Decisions & Trade-offs Log
*A record of critical decisions made during the architectural dialogue.*

- **Decision:** Chose the existing **OCI VPS** for deployment over a serverless platform like Google Cloud Run.
  - **Reason:** To leverage existing infrastructure that is already being maintained and with which the team is familiar. This is a pragmatic choice accepting the trade-off of manual server management in exchange for using a readily available asset.
- **Decision:** Chose **Google Cloud Storage** over Google Drive for data ingestion.
  - **Reason:** GCS provides a technically robust, secure, and reliable pipeline for backend services. It meets the **$0 cost requirement** for the MVP via its generous free tier, making it superior to the technically fragile and complex integration required for Google Drive.
- **Decision:** Explicitly chose **no database** for the MVP.
  - **Reason:** A database adds unnecessary complexity and development time. A simple `json` file combined with a strict file naming convention is sufficient to meet all requirements of the MVP scope and aligns with the principle of "Extreme Speed to Market."