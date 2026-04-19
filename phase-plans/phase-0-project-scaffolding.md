# Phase 0 Sub-Plan: Project Scaffolding

## Objective

Create a clean, reproducible repository skeleton that boots with Docker Compose and serves a healthy FastAPI endpoint.

## Entry criteria

- Master scope accepted as-is.
- No code assumed to exist beyond planning docs.

## Pre-implementation context checklist

- Confirm host details for implementation and verification:
  - OS: Windows 11 with Docker Desktop + WSL2.
  - Docker compose plugin available.
  - Nvidia GPU path expected for default compose.
- Confirm repository conventions:
  - Project/package name: polyglot.
  - Python version: 3.11.
  - Commit style: Conventional Commits.
- Confirm initial directory/file layout to create:
  - app/ (FastAPI app)
  - docs/ and docs/images/
  - tests/
  - .github/workflows/
- Confirm base dependencies and toolchain:
  - FastAPI, Uvicorn, structlog, SQLAlchemy, Alembic, pytest, pytest-asyncio, ruff, mypy.
- Confirm Docker constraints:
  - GPU required in docker-compose.yml.
  - docker-compose.cpu.yml override must remove GPU reservations and set DEVICE=cpu.

## Architecture choices to state before coding

1. Python packaging style:
   - Choice target: pyproject-only with pinned runtime/test/dev dependencies.
   - Alternative: split requirements files.
2. API app layout:
   - Choice target: app/main.py with routers and config modules.
   - Alternative: single-file app for minimal start.
3. Container user strategy:
   - Choice target: non-root runtime user in Dockerfile.
   - Alternative: root user for simpler permissions.

## Implementation sequence

1. Initialize repository structure and baseline metadata files.
2. Create pyproject.toml with tool configs for ruff and mypy.
3. Create Dockerfile based on nvidia/cuda:12.4.0-runtime-ubuntu22.04 with Python 3.11 and non-root user.
4. Create docker-compose.yml with backend + ollama, named volumes, backend dependency on ollama.
5. Create docker-compose.cpu.yml to disable GPU reservations.
6. Implement FastAPI skeleton endpoints:
   - GET /healthz -> {"status":"ok","version":"0.1.0"}
   - GET /metrics placeholder
   - structured JSON logging startup event
7. Add CI workflow running ruff, format check, mypy, pytest.
8. Add pre-commit config for ruff.
9. Create documentation stubs and initial CHANGELOG entry.

## Verification pack

Run and capture output:

```bash
# GPU path
docker compose up -d
curl http://localhost:8000/healthz
docker compose logs backend | head

# CPU override path
docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
```

Expected evidence:

- Health response returns status ok and version 0.1.0.
- Backend logs include startup event in JSON.
- CPU override starts without GPU reservation errors.
- GitHub Actions pipeline passes lint/type/test.

## Required documentation updates

- README.md: quickstart, prerequisites, env var placeholder table, Mermaid placeholder architecture.
- docs/architecture.md: high-level diagram and component roles.
- CONTRIBUTING.md: dev setup, test commands, commit convention.
- CHANGELOG.md: Phase 0 entry.

## Exit criteria

- Fresh clone boots and serves /healthz within 2 minutes (excluding initial image pull).
- CI is green.
- Docs render cleanly on GitHub.
- Stop and wait for explicit user approval.

## Known risks and mitigations

- Risk: Docker GPU configuration differs by host.
  - Mitigation: keep CPU override documented and tested in this phase.
- Risk: stale docs from day one.
  - Mitigation: phase gate requires README + architecture doc update before approval.
