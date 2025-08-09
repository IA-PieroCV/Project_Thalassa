# MVP Scope Definition: Project Thalassa
*This document defines the precise scope for the Minimum Viable Product. It is a companion to the main Business_Brief.md.*

---

## 1. Core Hypothesis to be Tested
*The single, most important assumption that this MVP is designed to validate in the market.*

**Hypothesis:** "A top-tier Chilean salmon producer will trust our 'SRS Outbreak Risk Score' enough to take it seriously and engage in a formal pilot, even without automated treatment recommendations."

---

## 2. The MVP Feature Set

### 2.1. IN-SCOPE Features (What we WILL build)
*A definitive checklist of features that constitute the MVP. This list is final for the first development cycle.*

- [ ] **Manual Data Ingestion (Concierge Service):**
    - [ ] Partner provides `fastq` files via a secure, shared cloud folder (e.g., Google Drive). No user-facing upload portal will be built.
- [ ] **Backend Analytics Engine:**
    - [ ] The core AI model that processes `fastq` files and generates the "SRS Outbreak Risk Score".
- [ ] **Simple Results Dashboard:**
    - [ ] A single, static, password-protected webpage.
    - [ ] Displays a simple list of the partner's sea cages and their corresponding current risk score (e.g., "Cage A1: 85% Risk").
- [ ] **Manual Email Alerts:**
    - [ ] The Thalassa team will manually email the partner contact when a risk score crosses a predefined critical threshold.

### 2.2. OUT-OF-SCOPE Features (What we will NOT build yet)
*An explicit list of features that are intentionally excluded to reduce complexity and speed up delivery. This is critical for preventing scope creep.*

- **Prescriptive Recommendations:** No suggestions on how to fix the underlying issue.
- **ROI Reporting & Dashboards:** No automated financial or operational impact reports.
- **Self-Service Portal:** No user-managed accounts, upload interfaces, or settings.
- **Interactive Map UI:** No geographical visualization of the sea cages.
- **Integration with Other Data Sources:** No inputs for host genetics, antibiotic history, or other farm data will be integrated at this stage.

---

## 3. Success Criteria for the MVP

### 3.1. Primary Success Metric
*The single most important number that will tell us if the MVP test was successful.*

**Metric:** "Secure a signed Letter of Intent (LOI) or formal pilot agreement from a target partner within 4 weeks of presenting them with the first risk scores generated from their own data."

### 3.2. Target Development Cycle
*The estimated time for a development team to build, test, and ship this MVP.*

**Estimate:** "3-4 week development cycle."