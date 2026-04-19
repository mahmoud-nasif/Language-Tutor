# Project: Polyglot — self-hosted pronunciation and grammar tutor (V1)

## What I'm building

A language tutor that evaluates my spoken **English (en-US)** and **German (Standard Hochdeutsch, tolerant of northern regional accent)**, and gives specific, actionable feedback on pronunciation, grammar, and fluency. Portfolio-grade: architecture, tests, and documentation carry equal weight with features.

## Working protocol

You are my pair programmer, not an autonomous builder. We will build this in phases. **At the end of each phase, run the verification steps, show me the output, and wait for my explicit approval before starting the next phase.** Never skip ahead. When any decision is ambiguous, stop and ask rather than guessing. When you are about to make an architectural choice (library, protocol, data model), state the choice and alternatives *before* implementing — I want to learn from the tradeoffs.

Commit small, logical units with Conventional Commits style messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Every phase ends with updated documentation and a `CHANGELOG.md` entry.

## Core principle: structured error detection, not vibes

The tutor must not rely on the LLM to judge pronunciation. The LLM only explains errors that the signal-processing layer has already detected. Concretely:

1. An ASR model (faster-whisper) gives us word-level transcription with timing and confidence.
2. A phoneme-level model (wav2vec2-phoneme) gives us the actual IPA phoneme sequence the user produced.
3. A G2P step converts the **target** sentence into its expected IPA phoneme sequence.
4. A deterministic aggregator does sequence alignment between expected and actual, and produces a structured JSON error report covering words, phonemes, timing, and fluency.
5. Only then does the LLM see the report and generate natural-language feedback.

This separation is **non-negotiable**. It is the project's core engineering contribution. The LLM is forbidden from inventing errors not present in the report.

## Target environment

- **Host:** any OS running Docker. Developed on Windows 11 + Docker Desktop (WSL2 backend). Must also work unchanged on Linux with Docker Engine, and on macOS with minor documented changes.
- **GPU:** Nvidia CUDA, always. The Nvidia Container Toolkit is assumed present on Linux; CUDA-on-WSL on Windows. The default `docker-compose.yml` requires GPU. A `docker-compose.cpu.yml` override must be provided and documented for CPU-only hosts (Macs, AMD boxes, GPU-less Linux), even though we will not actively develop against it in V1.
- **Audio capture:** browser-based via the Web Audio / MediaRecorder APIs. The backend never touches the host's audio device directly — this is how we sidestep USB passthrough headaches across OSes.
- **Browser:** current Chrome or Edge on the host at `http://localhost:8000`.
- **Python:** 3.11 inside the container.

### Cross-host portability notes (document these)

- **Windows 11:** Docker Desktop with WSL2 backend + CUDA-on-WSL. Works out of the box.
- **Linux:** Docker Engine + `nvidia-container-toolkit`. Works out of the box.
- **macOS (Apple Silicon):** no Nvidia. Use `docker-compose.cpu.yml`. Note the option to run Ollama natively on the host (Metal-accelerated) and point the backend at it via host-gateway; document this as an alternative path.
- **AMD GPU hosts:** not supported in V1. Document the intended path (llama.cpp with Vulkan, WhisperX on CPU) but do not implement.

## Scope for V1 (be strict about this)

- Two languages: **en-US** and **de-DE**. Explicit language switch in the UI; no auto-detection.
- **Northern-accent tolerance** for German is handled implicitly in V1 — Whisper and wav2vec2 de models already cope. Do **not** build explicit accent-aware scoring in V1, but add a `TODO.md` note for V2: per-user calibration and accent-aware phoneme substitution matrices.
- **Guided drill mode only.** User is shown a target sentence, reads it aloud, gets feedback. No free conversation, no open-ended dialog.
- Meta-language (the language of explanation) is user-selectable independent of practice language.
- Browser UI; no mobile app; no native desktop app.

## Technology choices

Use these unless you identify a blocker, in which case stop and raise it.

- **Backend framework:** FastAPI, with Uvicorn. Audio is sent via chunked HTTP POST for V1 (WebSocket streaming is a V2 concern).
- **ASR with word timing and confidence:** [WhisperX](https://github.com/m-bain/whisperX) using `faster-whisper` backend. Model: `small` multilingual on GPU. Upgradeable to `medium` via env var.
- **Phoneme recognition:**
  - English: `facebook/wav2vec2-lv-60-espeak-cv-ft` (outputs espeak-style phonemes).
  - German: `facebook/wav2vec2-large-xlsr-53-german` + post-processing to IPA. If the phoneme quality from this model proves insufficient during Phase 1 verification, stop and discuss alternatives (CLAP-IPA, MFA forced alignment + GOP scoring) before continuing.
- **G2P (target sentence → IPA):** [`phonemizer`](https://github.com/bootphon/phonemizer) with the espeak-ng backend. Supports both `en-us` and `de`.
- **Sequence alignment:** Needleman-Wunsch over phoneme sequences with an explicit, documented scoring matrix (match, mismatch, gap, with phonetic-similarity-aware substitution costs for common confusions like /θ/↔/t/, /v/↔/w/, German /ʁ/↔/r/).
- **LLM:**
  - **Primary: Ollama**, running in its own container with GPU access. Default model: `qwen2.5:7b-instruct` (Q4_K_M). Configurable via env var; document swapping to `qwen2.5:14b-instruct` (if VRAM allows) or `llama3.1:8b-instruct`.
  - **Fallback: Claude API** via the official Anthropic SDK (`anthropic` package).
  - Both exposed through the same `LLMProvider` abstract class. Provider selection via `LLM_PROVIDER` env var (`ollama` | `claude`), model selection via `LLM_MODEL`.
- **TTS:** [Piper](https://github.com/rhasspy/piper). Voices: `en_US-lessac-medium` and `de_DE-thorsten-medium`. CPU inference is fine.
- **Storage:** SQLite with SQLAlchemy 2.x. Migrations via Alembic. Database file in a named Docker volume.
- **Frontend:** plain HTML + vanilla JS + [Alpine.js](https://alpinejs.dev/) for reactivity + [Tailwind CSS via CDN](https://tailwindcss.com/docs/installation/play-cdn) for styling. No build step. No npm. Single `index.html` served by FastAPI via `StaticFiles`.
- **Testing:** pytest, with `pytest-asyncio` for async code. Audio fixtures committed to `tests/fixtures/`.
- **Linting/formatting:** `ruff` for lint + format. `mypy` in lenient mode.
- **CI:** GitHub Actions for lint + tests on push. No deployment.

## Documentation standards (this is portfolio-facing — take it seriously)

Every phase must leave documentation in a polished, GitHub-ready state. Never ship a phase with a stale README.

Required files and conventions:

- **`README.md`** at the root. Must include, in order:
  - Project name, one-line description, shields.io badges (license, CI status, Python version).
  - Animated GIF or screenshot of the working app (added once there's a UI).
  - Table of contents.
  - "Why this project" section (2–3 paragraphs on what's novel).
  - Architecture diagram (Mermaid in-line, or an SVG in `docs/images/` — use Mermaid initially).
  - Quickstart: prerequisites, clone, `docker compose up`, browser URL.
  - Configuration reference (env vars table).
  - How to swap LLM provider.
  - How to run on CPU-only hosts.
  - Development guide (run tests, update models, contribute).
  - License.
- **`docs/` folder** with per-component docs, each a standalone readable document:
  - `docs/architecture.md` — system overview with diagrams.
  - `docs/pipeline.md` — how audio becomes a report, step by step.
  - `docs/phoneme-analysis.md` — the G2P + alignment + scoring approach, with worked examples.
  - `docs/llm-providers.md` — how the adapter works, how to add a new provider, prompt design.
  - `docs/deployment.md` — host-specific notes (Windows, Linux, Mac, CPU-only).
  - `docs/data-model.md` — SQLite schema and rationale.
  - `docs/images/` — diagrams and screenshots.
- **`CHANGELOG.md`** following [Keep a Changelog](https://keepachangelog.com/) format. One entry per phase minimum.
- **`CONTRIBUTING.md`** — how to set up a dev environment, run tests, commit conventions.
- **`LICENSE`** — MIT.
- **`TODO.md`** — living list of V2 ideas and known limitations.
- **`.github/`** — CI workflow, issue templates, pull request template.

Tone in docs: clear, technical, honest about limitations. Never marketing-speak. Diagrams where they clarify, prose where diagrams don't.

## Structured error report schema (lock this in Phase 1)

```json
{
  "target": "I've been living here for three years",
  "language": "en-US",
  "transcribed": "I been living here for tree years",
  "word_alignment": [
    {"expected": "I've", "got": "I", "type": "contraction_missed", "start_ms": 120, "end_ms": 280},
    {"expected": "three", "got": "tree", "type": "substitution",
     "expected_ipa": "θriː", "actual_ipa": "triː",
     "phoneme_errors": [{"expected": "θ", "got": "t", "category": "dental_fricative_stopping"}]}
  ],
  "fluency": {
    "duration_ms": 4200,
    "speech_rate_wpm": 95,
    "long_pauses_ms": [850],
    "filler_count": 0
  },
  "overall": {
    "word_error_rate": 0.14,
    "phoneme_error_rate": 0.08,
    "intelligibility_score": 0.82
  }
}
```

This schema is the contract between the analysis layer and the LLM. Version it (`"schema_version": 1`) and treat changes as breaking.

---

## Build phases

### Phase 0 — Project scaffolding

**Goal:** a clean, reproducible repo skeleton that boots with `docker compose up` and responds to a health check.

**Tasks:**
- Initialize Git repo, `.gitignore` (Python, IDE, Docker, model caches, SQLite).
- Create `pyproject.toml` (package name `polyglot`, Python 3.11, pinned dependencies, ruff + mypy config).
- Create `Dockerfile` using `nvidia/cuda:12.4.0-runtime-ubuntu22.04` base with Python 3.11 installed, non-root user, layer caching friendly.
- Create `docker-compose.yml` with two services: `backend` (GPU reservation via `deploy.resources.reservations.devices`) and `ollama` (official `ollama/ollama` image with GPU). Named volumes for `hf-cache`, `ollama-models`, `app-data`. Backend depends on ollama.
- Create `docker-compose.cpu.yml` override that strips GPU reservations and sets `DEVICE=cpu` env var.
- Create FastAPI app skeleton with `/healthz` returning `{"status": "ok", "version": "0.1.0"}`, structured JSON logging via `structlog`, and `/metrics` placeholder.
- Create `.github/workflows/ci.yml` running `ruff check`, `ruff format --check`, `mypy`, and `pytest` on push and PR.
- Create `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE` (MIT), `TODO.md`, and `docs/` folder with stub files.
- Add pre-commit hook config (`.pre-commit-config.yaml`) running ruff.

**Deliverables:**
- Repo that clones, builds, and runs with two commands.
- CI green on first commit.

**Expected output:**
```
$ docker compose up -d
$ curl http://localhost:8000/healthz
{"status":"ok","version":"0.1.0"}
$ docker compose logs backend | head
{"event":"startup","level":"info","timestamp":"..."}
```

**How to verify:**
1. I clone the repo fresh, run `docker compose up`, and get a healthy endpoint within 2 minutes (excluding first-time image pull).
2. I run `docker compose -f docker-compose.yml -f docker-compose.cpu.yml up` and it starts without GPU.
3. CI passes on GitHub.
4. `README.md` renders cleanly on GitHub with a proper table of contents and a placeholder architecture diagram in Mermaid.

**Documentation required:** initial README (quickstart, env vars placeholder), `docs/architecture.md` with high-level diagram, `CHANGELOG.md` entry, `CONTRIBUTING.md` with dev setup.

**STOP. Show me the output of the verification steps. Wait for approval.**

---

### Phase 1 — Analysis pipeline (headless)

**Goal:** a single endpoint that takes a WAV upload plus a target sentence and returns the structured JSON error report. No UI, no LLM.

**Tasks:**
- Audio preprocessing module: load WAV, resample to 16 kHz mono, normalize, return numpy array. Handle common failure modes (too short, silence, clipping).
- WhisperX integration with CUDA. Returns word-level transcription with timestamps and word-level confidence.
- wav2vec2 phoneme recognition module (CUDA) for both languages. Output espeak-format phonemes, then convert to IPA via a documented mapping table.
- G2P module using `phonemizer` + espeak-ng for both languages; produces expected IPA sequence for target.
- Alignment module implementing Needleman-Wunsch over phoneme sequences. Document the scoring matrix in `docs/phoneme-analysis.md`, including the phonetic-similarity substitution costs.
- Error aggregator that combines word-level and phoneme-level alignment into the V1 schema, including fluency metrics (speech rate from WhisperX timestamps, pause detection, filler-word detection via a simple list per language).
- `POST /analyze` endpoint: multipart form accepting a WAV file and `target_sentence` + `language` fields. Returns the error report JSON.
- pytest suite:
  - Unit tests for alignment with synthetic inputs.
  - Integration tests with 4 English + 4 German audio fixtures (committed to repo or stored in Git LFS). Cases: clean read, word substitution, phoneme substitution, long pause.
  - Golden-file assertions on report structure.

**Deliverables:**
- Working `/analyze` endpoint.
- 8+ audio fixtures with expected reports.
- Test suite, all green.
- `docs/pipeline.md` and `docs/phoneme-analysis.md` complete with worked examples.

**Expected output:**
```
$ curl -F "audio=@my_clip.wav" -F "target_sentence=Ich wohne in Hamburg" \
       -F "language=de-DE" http://localhost:8000/analyze | jq
{
  "schema_version": 1,
  "target": "Ich wohne in Hamburg",
  "language": "de-DE",
  "transcribed": "Ich wohne in Hamburg",
  "word_alignment": [...],
  "fluency": {...},
  "overall": {...}
}
```

**How to verify:**
1. I will record 4–6 fresh clips in each language — some clean, some with deliberate errors I'll list out ahead of time (e.g. "I said *tree* instead of *three*"). We run them through `/analyze` and confirm each deliberate error shows up in the report.
2. I pick a clip where Whisper transcribes cleanly but I know I mispronounced a phoneme — the phoneme layer should catch it even when the word layer doesn't.
3. I run `pytest` locally and see all green.
4. `docs/phoneme-analysis.md` contains at least two worked examples (one per language) stepping from audio to report.

**Documentation required:** `docs/pipeline.md` (full pipeline walkthrough), `docs/phoneme-analysis.md` (G2P, alignment, scoring matrix), README update (architecture diagram now populated, env vars table, analyze endpoint documented), CHANGELOG entry.

**STOP. I will test with real recordings. Do not start Phase 2 until I confirm the reports are sensible for both languages.**

---

### Phase 2 — LLM feedback layer

**Goal:** the error report becomes natural-language feedback, via a local LLM by default.

**Tasks:**
- Define `LLMProvider` abstract base class: `async generate(report: dict, meta_language: str) -> FeedbackResponse`. `FeedbackResponse` is a Pydantic model with `summary`, `per_error_explanations`, `encouragement`, `next_suggestion`.
- Implement `OllamaProvider`: talks to the `ollama` service via its OpenAI-compatible endpoint, uses `LLM_MODEL` env var (default `qwen2.5:7b-instruct`).
- Implement `ClaudeProvider`: uses `anthropic` SDK, `ANTHROPIC_API_KEY` env var, model configurable.
- Provider factory picks from `LLM_PROVIDER` env var.
- System prompt engineered carefully: supplies the report as structured JSON, instructs the model to only explain what's in the report, forbids fabrication, asks for output in `meta_language`, specifies output as JSON matching `FeedbackResponse`. Include few-shot examples in the prompt. Store the prompt in `app/llm/prompts/feedback_v1.md` with a header comment explaining the design.
- `POST /feedback` endpoint: takes the report, returns `FeedbackResponse`.
- Integration test that mocks both providers and asserts the contract holds.
- On-startup check that pulls the default Ollama model if not present (or fails with a clear error).

**Deliverables:**
- Working `/feedback` endpoint.
- Both providers functional.
- System prompt checked in as a readable document.
- Tests.

**Expected output:**
```
$ curl -X POST -H "Content-Type: application/json" \
    -d @sample_report.json http://localhost:8000/feedback | jq
{
  "summary": "Good attempt. One pronunciation issue on 'three' and a missed contraction.",
  "per_error_explanations": [
    {"word": "I've", "explanation": "You said 'I' — in English, 'I have' contracts to 'I've' in casual speech..."},
    {"word": "three", "explanation": "The 'th' sound in English is a dental fricative /θ/; you produced /t/..."}
  ],
  "encouragement": "Your fluency and pacing were natural.",
  "next_suggestion": "Try a drill targeting th-sounds: 'three thin thieves'."
}
```

**How to verify:**
1. I hand-craft 3 synthetic error reports covering different error types and run them through both providers; we compare quality side by side.
2. I feed a report with **no errors** and confirm the LLM says so rather than inventing errors (this is the hallucination test — if this fails, the prompt is wrong).
3. I run with `meta_language=de-DE` on an English error report and confirm feedback is in German.
4. I confirm `ollama ps` shows the model loaded on the GPU.

**Documentation required:** `docs/llm-providers.md` (adapter contract, how to add providers, model selection guidance, VRAM table), prompt file checked in with design notes, README updated with provider configuration, CHANGELOG entry.

**STOP. I will test both providers side by side and confirm feedback quality before Phase 3.**

---

### Phase 3 — Web UI for guided drills

**Goal:** a usable browser UI for the full flow.

**Tasks:**
- `app/frontend/index.html` + Alpine.js state + Tailwind CDN. Single page, no build.
- Language picker (en-US / de-DE) and meta-language picker.
- Drill library panel: loads list from `GET /drills?language=...`, organized by difficulty and skill tag. Seed with 10 drills per language committed to `app/drills/` as JSON.
- Target sentence display with "play reference" button (stub in this phase, wired in Phase 5).
- Record button using MediaRecorder API; shows live VU meter; stop button.
- On stop, POSTs audio to `/analyze` → passes report to `/feedback` → renders result.
- Results view: target sentence with color-coded spans (green = good, yellow = minor issue, red = error), IPA shown on hover for flagged phonemes, LLM feedback below, replay-your-recording button.
- Loading states and error toasts.

**Deliverables:**
- Working end-to-end browser flow.
- Seeded drill library.
- Screenshot and 10-second GIF added to README.

**Expected output:** I open `http://localhost:8000`, pick German, pick a drill, record, see annotated results with LLM feedback within ~10 seconds of stopping.

**How to verify:**
1. I walk through the full flow in both languages.
2. I deliberately make specific errors and confirm the UI highlights the right spans.
3. I test on Chrome and Edge on Windows; note any cross-browser issues.
4. I confirm the mic permission flow is clean and that denied permissions produce a helpful error.

**Documentation required:** `docs/ui.md` (UI structure, state model, how drills are defined), README screenshot + GIF, CHANGELOG entry.

**STOP. End-to-end demo. Approve before Phase 4.**

---

### Phase 4 — Session history and progress

**Goal:** persistent history, and at least one useful progress view.

**Tasks:**
- SQLAlchemy models: `Drill`, `Attempt`, `ErrorInstance` (phoneme-level, linked to attempt).
- Alembic migrations.
- `POST /analyze` now persists an `Attempt` row; feedback persistence on `/feedback` completion.
- `GET /history` endpoint.
- `GET /progress/phonemes?language=...` aggregating error rates per phoneme over time.
- UI: history list view, phoneme error rate chart (use lightweight [uPlot](https://github.com/leeoniya/uPlot) or similar, no heavy chart library).
- Export endpoint: `GET /export` returns full history as JSON.

**Deliverables:**
- Persistent sessions surviving container restarts.
- History UI, progress chart.
- Export.

**Expected output:** after 5+ practice sessions, I see a history list and a chart of, say, my /θ/ error rate declining over time (or not — honest data).

**How to verify:**
1. I do 5 sessions, `docker compose down && docker compose up`, confirm data persists.
2. I spot-check rows in SQLite match what I actually did.
3. I deliberately make a specific phoneme error repeatedly and watch it appear on the progress chart.
4. `GET /export` returns valid JSON.

**Documentation required:** `docs/data-model.md` (schema + rationale + ER diagram in Mermaid), README updated with history/progress screenshots, CHANGELOG entry.

**STOP.**

---

### Phase 5 — Polish and hardening

**Goal:** portfolio-ready. Someone can clone, run, and understand this in 15 minutes.

**Tasks:**
- Piper TTS integration for reference sentence playback and optional spoken feedback. Cache generated audio by `(sentence, voice)` hash.
- Expanded drill library: 25+ per language, tagged by skill (e.g. `th-sounds`, `dative-prepositions`, `umlauts`, `r-sound`). Drills as JSON with metadata.
- Latency instrumentation at every pipeline boundary; `/metrics` endpoint exposes p50/p95 for each stage over the last N requests.
- Robust error handling: mic access denied, model timeout, empty audio, silence-only audio, too-long audio, Ollama unreachable, Claude API quota hit.
- A "demo mode" that seeds 20 synthetic sessions so a portfolio reviewer can see the progress chart without doing 20 sessions themselves.
- README completed: full screenshots, architecture diagram updated, clear "how it works" section for non-technical reviewers, performance characteristics table, limitations and V2 roadmap section.
- `docs/deployment.md` fully written: Windows, Linux, Mac (CPU override), AMD note.
- Final CI check: on a GitHub Actions runner with no GPU, the CPU override config at least builds and passes unit tests (integration tests can be GPU-gated).

**Deliverables:**
- Portfolio-ready repo.
- Working CPU override (tests pass).

**Expected output:** someone else on a different OS follows the README and has it running in 15 minutes. A recruiter looking at the README understands the project in 3 minutes.

**How to verify:**
1. I wipe my Docker state and follow my own README from scratch.
2. I hand the GitHub link to one person and they can run it without asking me for help.
3. All `/metrics` latencies show reasonable numbers; none are missing.
4. I unplug my network cable and the whole app still works end to end (proving offline local-LLM path).
5. CI is green; the CPU-override job also green for unit tests.

**Documentation required:** everything complete. `README.md`, `docs/architecture.md`, `docs/pipeline.md`, `docs/phoneme-analysis.md`, `docs/llm-providers.md`, `docs/deployment.md`, `docs/data-model.md`, `docs/ui.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `TODO.md`. Add a short `BLOG.md` or link to a writeup explaining what I learned — this is the portfolio hook.

**STOP. Ship.**

---

## Start

Begin with Phase 0. Before touching the filesystem:

1. Summarize in 8–12 bullets what you are about to build and why, so I can catch misunderstandings early.
2. List every clarifying question you have.
3. Flag any concern about the tech choices.

Then wait for my reply.