# Polyglot Implementation Sub-Plans

This folder breaks the master plan into start-ready phase documents.

## How to use these docs

1. Open the phase document you are about to implement.
2. Complete the "Pre-implementation context checklist" first.
3. Confirm "Architecture choices to state before coding" with the user.
4. Implement in the listed sequence with small Conventional Commits.
5. Run the verification pack and capture output.
6. Update required docs and CHANGELOG.
7. Stop and request explicit approval before the next phase.

## Phase map

- Phase 0: [phase-0-project-scaffolding.md](phase-0-project-scaffolding.md)
- Phase 1: [phase-1-analysis-pipeline.md](phase-1-analysis-pipeline.md)
- Phase 2: [phase-2-llm-feedback.md](phase-2-llm-feedback.md)
- Phase 3: [phase-3-web-ui.md](phase-3-web-ui.md)
- Phase 4: [phase-4-history-progress.md](phase-4-history-progress.md)
- Phase 5: [phase-5-polish-hardening.md](phase-5-polish-hardening.md)

## Dependency order

- Phase 0 is required before all other phases.
- Phase 1 depends on Phase 0.
- Phase 2 depends on Phase 1.
- Phase 3 depends on Phases 1 and 2.
- Phase 4 depends on Phase 3.
- Phase 5 depends on Phase 4.

## Global non-negotiables carried into every phase

- Keep deterministic analysis separate from LLM explanation.
- Do not start a new phase without user approval.
- End each phase with verification output, docs updates, and CHANGELOG entry.
- Use Docker-first workflow and keep GPU default plus CPU override path.
