# Changelog

All notable changes to Project Thalassa will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [Added]: Bearer Token authentication for secure upload endpoints (#25)
- [Added]: FastAPI endpoint for fastq file uploads with validation and secure storage (#24)
- [Added]: Modern development environment with pixi package manager (#43)
- [Added]: Comprehensive testing framework with pytest and async support (#43)
- [Added]: Docker containerization with multi-stage builds (#43)
- [Added]: Code quality tooling with ruff, pre-commit hooks (#43)
- [Added]: FastAPI application foundation and project structure (#43)
- MkDocs documentation system with Material theme
- Auto-generated API documentation with mkdocstrings
- Comprehensive project documentation structure
- Multi-stage Docker build optimization

### Changed
- Upgraded Dockerfile to use pixi-docker multi-stage build pattern
- Updated project structure documentation in README
- Modernized development workflow documentation

### Removed
- Legacy `run_dev.py` development server launcher
- Outdated references to old storage structure

## [0.1.0] - 2024-01-XX

### Added
- Initial FastAPI application structure
- Pixi package manager integration
- Modern development toolchain (ruff, ty, pytest)
- Basic project configuration and environment setup
- Docker containerization support
- Comprehensive testing framework with pytest-asyncio
- Pre-commit hooks for code quality

### Infrastructure
- Pixi-based dependency management
- Ruff for linting and formatting
- Ty for fast type checking
- pytest with async support and coverage
- Pre-commit hooks for automated quality checks

---

## Release Process

1. Update version numbers in `pixi.toml`
2. Update this changelog with release notes
3. Create a git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tags: `git push origin --tags`
