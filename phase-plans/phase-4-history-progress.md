# Phase 4 Sub-Plan: Session History and Progress

## Objective

Persist attempts and errors, expose history/export APIs, and provide at least one meaningful progress visualization (phoneme error rate over time).

## Entry criteria

- Phase 3 completed and approved.
- End-to-end analysis and feedback loop already working.

## Pre-implementation context checklist

- Confirm persistence stack:
  - SQLite in Docker named volume.
  - SQLAlchemy 2.x models.
  - Alembic migrations required.
- Confirm entities and relationships:
  - Drill
  - Attempt
  - ErrorInstance (phoneme-level, tied to Attempt)
- Confirm API requirements:
  - GET /history
  - GET /progress/phonemes?language=...
  - GET /export
- Confirm charting constraints:
  - lightweight chart library only (uPlot preferred).
- Confirm persistence boundaries:
  - /analyze should persist Attempt.
  - /feedback completion should persist feedback payload or derived text fields.

## Architecture choices to state before coding

1. Data retention granularity:
   - Choice target: store raw report JSON plus normalized key fields for query efficiency.
   - Alternative: store only normalized rows.
2. Progress aggregation strategy:
   - Choice target: compute per-phoneme error rate over sliding chronological windows.
   - Alternative: cumulative all-time aggregate only.
3. Export schema:
   - Choice target: versioned export envelope with metadata and arrays.
   - Alternative: raw table dumps.

## Implementation sequence

1. Define SQLAlchemy models and relationships.
2. Generate and review Alembic migration scripts.
3. Add persistence hooks in analyze and feedback flow.
4. Implement GET /history with pagination and basic filters.
5. Implement GET /progress/phonemes aggregation endpoint.
6. Implement GET /export as full JSON export endpoint.
7. Extend UI with:
   - history list
   - phoneme progress chart
8. Add tests for:
   - migration application
   - persistence on analyze/feedback
   - endpoint response schemas
   - export validity

## Verification pack

Run and capture evidence:

```bash
# perform 5+ sessions manually
docker compose down
docker compose up -d
curl http://localhost:8000/export | jq
```

Human verification scenarios:

- Data survives container restart.
- History view matches actual attempts.
- Repeated deliberate phoneme error appears in progress chart trend.
- Export endpoint returns valid, parseable JSON.

Expected evidence:

- Persistent records across restarts.
- Correct endpoint outputs for history/progress/export.
- Chart updates after new sessions.

## Required documentation updates

- docs/data-model.md: schema rationale and Mermaid ER diagram.
- README.md: history/progress screenshots and feature notes.
- CHANGELOG.md: Phase 4 entry.

## Exit criteria

- Persistence verified across restarts.
- Progress chart provides meaningful trend visibility.
- Export endpoint complete and valid.
- Stop and wait for explicit user approval.

## Known risks and mitigations

- Risk: migration drift across environments.
  - Mitigation: run migration tests in CI and document reset strategy.
- Risk: query performance degradation with large history.
  - Mitigation: indexes on attempt timestamp, language, and phoneme columns.
