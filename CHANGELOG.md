# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0

### Added
- [Strategic]: Created GitHub issue #64 for MVP v1.0.0 official release management and partner presentation preparation
- [Feature]: AnalysisService class for fastq file discovery and metadata extraction (#28)
- [Feature]: Basic FastAPI application skeleton with template and static file support (#34)
- [Testing]: Comprehensive integration tests for authenticated dashboard endpoint (#36)
- [Improvement]: Enhanced workflow file management and branch creation safety (workflow-fixes)
- [Feature]: Core SRS risk analysis model integration with multi-factor algorithm (#30)
- [Feature]: Dashboard endpoint logic to read and parse results.json files with live analysis fallback (#38)
- [Feature]: Batch analysis script for results.json generation with comprehensive unit tests (#31)
- [Feature]: Dashboard template dynamically renders risk scores with Jinja2 from results.json data (#39)
- [Testing]: Comprehensive integration test for dashboard data rendering with mock results.json validation (#40)
- [Documentation]: Critical alert email template with complete usage instructions and example (#42)
- [Feature]: Console logging for critical risk scores with threshold-based alerts and actionable guidance (#41)
- [Documentation]: Partner API guide for uploading data via API with authentication and troubleshooting (#26)
- [Documentation]: Comprehensive Bearer Token security guide with partner communication protocols (#37)
- [Testing]: Enhanced unit tests for filename parser and JSON formatter with comprehensive edge case validation (#32)
- [Testing]: Integration test for authenticated file upload with HTTP client validation and filesystem verification (#27)

### Changed

### Fixed
- [DevOps]: Single Dockerfile for combined FastAPI & analysis application with proper scripts access (#33)

### Removed
