# Phase 3 Sub-Plan: Web UI for Guided Drills

## Objective

Deliver a single-page browser UI that runs the full guided drill loop: choose drill, record audio, analyze, generate feedback, and display annotated results.

## Entry criteria

- Phase 2 completed and approved.
- Backend endpoints available:
  - GET /healthz
  - POST /analyze
  - POST /feedback

## Pre-implementation context checklist

- Confirm frontend constraints:
  - Single app/frontend/index.html.
  - Alpine.js + Tailwind CDN.
  - No npm and no build step.
- Confirm drill content contract:
  - 10 drills per language minimum.
  - Stored in app/drills/ as JSON with difficulty and skill tags.
- Confirm browser API behavior assumptions:
  - MediaRecorder for audio capture.
  - Web Audio for VU meter.
  - Chrome and Edge as target browsers.
- Confirm result rendering contract from analysis + feedback:
  - word alignment categories map to highlight colors.
  - IPA details available for flagged phoneme items.

## Architecture choices to state before coding

1. Frontend state model:
   - Choice target: centralized Alpine state object with explicit finite states (idle, recording, analyzing, showing_results, error).
   - Alternative: ad-hoc reactive fields without state machine semantics.
2. Drill source loading path:
   - Choice target: backend endpoint GET /drills?language=... reading JSON files server-side.
   - Alternative: static fetch directly from frontend.
3. Annotation rendering strategy:
   - Choice target: map alignment report to token-level UI view model first.
   - Alternative: direct template logic over raw report JSON.

## Implementation sequence

1. Create frontend shell and layout in app/frontend/index.html.
2. Implement Alpine state for language/meta-language, drill selection, recording state, result state, and error state.
3. Add drill library endpoint and seed data files for both languages.
4. Implement microphone permission and recording flow via MediaRecorder.
5. Add live VU meter based on audio analyser node.
6. On recording stop:
   - send audio + target + language to /analyze
   - send report + meta_language to /feedback
7. Render result components:
   - color-coded target spans
   - IPA hover details for flagged phonemes
   - feedback sections from feedback response
   - replay recorded audio
8. Implement loading states and toast-style error handling.
9. Add cross-browser checks for Chrome and Edge.

## Verification pack

Run and capture evidence:

```bash
# service already running
# open browser manually
http://localhost:8000
```

Human verification scenarios:

- Complete flow in en-US and de-DE.
- Deliberate pronunciation and word errors should map to expected highlighted spans.
- Denied mic permissions must show actionable error text.
- Response appears within about 10 seconds after recording stop under normal conditions.

Expected evidence:

- Functional drill selection and recording in both target languages.
- Correctly annotated result view with LLM feedback.
- Stable behavior on Chrome and Edge.

## Required documentation updates

- docs/ui.md: page structure, state model, recording flow, result rendering.
- README.md: UI screenshot and short GIF demo.
- CHANGELOG.md: Phase 3 entry.

## Exit criteria

- End-to-end guided drill workflow is usable in browser.
- Error handling for common UI failures is present.
- Visual annotation is understandable and tied to report data.
- Stop and wait for explicit user approval.

## Known risks and mitigations

- Risk: browser codec/container mismatch for uploaded audio.
  - Mitigation: constrain recording settings and normalize server-side.
- Risk: UI complexity in single HTML file.
  - Mitigation: modularize script sections and use clear state transitions.
