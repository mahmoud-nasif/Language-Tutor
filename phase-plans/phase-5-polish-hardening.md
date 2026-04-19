# Phase 5 Sub-Plan: Polish and Hardening

## Objective

Make the project portfolio-ready: robust UX/error handling, reference TTS, expanded drills, meaningful metrics, complete documentation, and CPU-override CI confidence.

## Entry criteria

- Phase 4 completed and approved.
- Core app flow stable in both languages.

## Pre-implementation context checklist

- Confirm final-scope additions:
  - Piper TTS integration for reference sentence playback.
  - Expanded drill library: 25+ per language with skill tags.
  - Metrics with stage latency p50/p95.
  - Demo mode with synthetic sessions.
- Confirm hardening failure modes to cover:
  - mic denied
  - model timeout
  - empty/silence audio
  - too-long audio
  - Ollama unreachable
  - Claude quota failure
- Confirm deployment docs breadth:
  - Windows, Linux, macOS CPU override, AMD unsupported note.
- Confirm offline requirement:
  - app remains usable with local Ollama when network is disconnected.

## Architecture choices to state before coding

1. TTS caching design:
   - Choice target: file cache keyed by hash(sentence, voice) with metadata index.
   - Alternative: DB-backed cache records only.
2. Metrics store strategy:
   - Choice target: in-memory rolling window for last N requests exposed at /metrics.
   - Alternative: persisted metrics table.
3. Demo mode activation:
   - Choice target: explicit env flag with idempotent synthetic seeding endpoint/script.
   - Alternative: automatic seeding at startup.

## Implementation sequence

1. Integrate Piper for reference playback and optional spoken feedback.
2. Add deterministic cache for generated TTS files.
3. Expand drill corpus to 25+ per language with consistent metadata.
4. Implement latency instrumentation at each stage:
   - preprocess
   - ASR
   - phoneme
   - G2P
   - alignment/aggregation
   - feedback generation
5. Implement /metrics p50/p95 summaries over recent requests.
6. Harden error handling and user-facing messages for all known failure modes.
7. Implement demo mode synthetic history seeding (20 sessions).
8. Complete all remaining docs and README polish.
9. Update CI to validate CPU override build + unit tests on non-GPU runner.

## Verification pack

Run and capture evidence:

```bash
# clean local state test
docker compose down -v
docker compose up -d

# cpu override CI-like check
docker compose -f docker-compose.yml -f docker-compose.cpu.yml build
docker compose -f docker-compose.yml -f docker-compose.cpu.yml run --rm backend pytest -m "not gpu"

# metrics check
curl http://localhost:8000/metrics
```

Human verification scenarios:

- Fresh setup from README works within 15 minutes.
- Third-party tester can run with no direct support.
- Offline mode works with local Ollama path.
- Metrics include expected stages and percentile values.

Expected evidence:

- Stable app behavior with robust failure messaging.
- CPU override path validated in CI for unit tests.
- Documentation is complete and coherent for portfolio review.

## Required documentation updates

- README.md: final screenshots/GIF, architecture, quickstart, performance table, limitations, V2 roadmap.
- docs/architecture.md
- docs/pipeline.md
- docs/phoneme-analysis.md
- docs/llm-providers.md
- docs/deployment.md
- docs/data-model.md
- docs/ui.md
- CONTRIBUTING.md
- TODO.md
- CHANGELOG.md
- BLOG.md or README link to writeup.

## Exit criteria

- New user can clone and run quickly on supported hosts.
- Offline local LLM path works end-to-end.
- Metrics and hardening checks pass.
- Documentation set is complete and accurate.
- Project is ready to ship.

## Known risks and mitigations

- Risk: final-phase sprawl and unfinished polish tasks.
  - Mitigation: treat docs and hardening as first-class deliverables, not cleanup.
- Risk: CPU path regressions hidden by GPU-first development.
  - Mitigation: explicit CPU override CI job and local verification checklist.
