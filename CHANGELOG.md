# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.2.0] - 2026-04-19

### Added

- Phase 1 deterministic analysis pipeline with audio preprocessing, WhisperX ASR integration, wav2vec2 phoneme recognition, and phonemizer G2P.
- Needleman-Wunsch phoneme alignment with explicit scoring matrix and similarity-aware substitution costs.
- `POST /analyze` endpoint returning schema-versioned structured report.
- Unit tests for alignment plus integration tests with 8 WAV fixtures and golden JSON assertions.
- Documentation updates for pipeline flow and phoneme analysis method.

## [0.1.0] - 2026-04-19

### Added

- Phase 0 project scaffolding with src-based package layout.
- FastAPI baseline service with /healthz and Prometheus /metrics endpoints.
- Structured JSON logging via structlog.
- Docker setup with GPU-first compose and CPU override compose.
- CI workflow for lint, format, type checks, tests, import-linter, and Docker build.
- Initial documentation set and contribution templates.
