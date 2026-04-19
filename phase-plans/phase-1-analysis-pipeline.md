# Phase 1 Sub-Plan: Analysis Pipeline (Headless)

## Objective

Deliver POST /analyze that accepts WAV + target sentence + language and returns schema_version=1 structured error report without any LLM dependency.

## Entry criteria

- Phase 0 completed and approved.
- Containerized environment and CI available.

## Pre-implementation context checklist

- Confirm frozen report contract (breaking-change sensitive):
  - schema_version included and set to 1.
  - sections: target, language, transcribed, word_alignment, fluency, overall.
- Confirm supported languages and locale codes:
  - en-US and de-DE only.
- Confirm model and library choices:
  - WhisperX (faster-whisper backend) for word timings/confidence.
  - wav2vec2 models for phoneme extraction.
  - phonemizer + espeak-ng for target G2P.
- Confirm performance/runtime assumptions:
  - CUDA path primary for ASR/phoneme inference.
  - CPU fallback not optimization target in V1.
- Confirm test fixture strategy:
  - At least 8 fixtures total (4 EN, 4 DE).
  - Include clean read, word substitution, phoneme substitution, long pause.

## Architecture choices to state before coding

1. IPA mapping normalization design:
   - Choice target: explicit mapping table file versioned in repo.
   - Alternative: inline mapping logic inside model modules.
2. Alignment implementation boundaries:
   - Choice target: standalone pure function module with deterministic inputs/outputs.
   - Alternative: embed alignment logic directly in aggregator.
3. Error typing taxonomy:
   - Choice target: explicit enum-like constants for error categories.
   - Alternative: free-form string labels.

## Implementation sequence

1. Add audio preprocessing module:
   - WAV ingest, resample 16k mono, normalize amplitude.
   - Handle too-short, silence-only, clipping warnings.
2. Integrate WhisperX inference wrapper returning:
   - transcript text
   - word-level start/end timestamps
   - confidence per token
3. Implement phoneme recognition wrappers per language.
4. Add phoneme output normalization and conversion to IPA via mapping table.
5. Add G2P module using phonemizer + espeak-ng for expected IPA.
6. Implement Needleman-Wunsch alignment with documented scoring matrix:
   - match, mismatch, gap
   - lower substitution penalties for common confusion pairs
7. Implement aggregator merging word-level and phoneme-level signals into schema.
8. Add fluency metric extraction:
   - speech rate from transcript and timing
   - long pauses from timing gaps
   - filler count from language-specific list
9. Add POST /analyze multipart endpoint.
10. Add unit tests for alignment and schema assembly.
11. Add integration tests and golden files for fixture outputs.

## Verification pack

Run and capture output:

```bash
curl -F "audio=@sample.wav" \
     -F "target_sentence=Ich wohne in Hamburg" \
     -F "language=de-DE" \
     http://localhost:8000/analyze | jq
pytest
```

Human verification scenarios:

- Deliberate error clips must surface expected errors.
- A clip with clean word transcription but known phoneme mispronunciation must still flag phoneme error.

Expected evidence:

- Response matches schema and includes schema_version=1.
- Tests pass, including golden-file checks.
- Worked examples exist in docs for both languages.

## Required documentation updates

- docs/pipeline.md: end-to-end data flow from audio input to report.
- docs/phoneme-analysis.md: G2P, mapping, alignment scoring matrix, two worked examples.
- README.md: architecture update, /analyze usage, env vars.
- CHANGELOG.md: Phase 1 entry.

## Exit criteria

- /analyze is functional for en-US and de-DE.
- 8+ fixtures committed and tested.
- Error report quality validated with real recordings.
- Stop and wait for explicit user approval.

## Known risks and mitigations

- Risk: German phoneme model quality may be insufficient.
  - Mitigation: pause after Phase 1 verification and review alternatives before moving on.
- Risk: drift between JSON schema and implementation.
  - Mitigation: lock Pydantic model + golden files with schema_version checks.
