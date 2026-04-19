# Contributing

## Development setup

1. Install uv.
2. Run uv sync --group dev.
3. Copy .env.example to .env.

## Validation commands

- uv run ruff check .
- uv run ruff format --check .
- uv run mypy src
- uv run pytest
- uv run lint-imports

## Commit conventions

Use Conventional Commits:

- feat:
- fix:
- docs:
- refactor:
- test:
- chore:
- ci:

## Architecture invariants

These layering rules are enforced in CI with import-linter:

- polyglot.analysis must not import polyglot.api.
- polyglot.storage must not import polyglot.llm.

Add new contracts when introducing new package boundaries.
