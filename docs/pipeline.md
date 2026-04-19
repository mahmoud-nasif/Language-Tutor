# Pipeline

Phase 1 adds a deterministic headless analysis pipeline behind `POST /analyze`.

## Inputs

- `audio`: WAV upload (multipart form)
- `target_sentence`: reference sentence to evaluate
- `language`: `en-US` or `de-DE`

## Processing stages

1. Audio preprocessing
	- Decode WAV.
	- Convert to mono 16 kHz.
	- Normalize amplitude.
	- Reject invalid clips (empty, too short, too long, silence-only).
2. ASR with timing
	- WhisperX transcribes audio.
	- Extract per-word start/end timestamps and confidence.
3. Phoneme recognition
	- wav2vec2 model per language outputs raw phoneme-like sequence.
	- Language-specific normalization converts output to IPA-compatible symbols.
4. Target G2P
	- phonemizer (espeak backend) converts target sentence to expected IPA by word.
	- A second G2P pass converts transcript words for substitution comparisons.
5. Sequence alignment
	- Needleman-Wunsch aligns expected and actual phoneme sequences.
	- Scoring matrix uses explicit match, mismatch, and gap values.
6. Aggregation
	- Word-level alignment built from deterministic sequence matching.
	- Phoneme-level mismatches attached where relevant.
	- Fluency metrics computed from timing (speech rate, long pauses, filler count).
7. Report assembly
	- Output validated against schema version 1 contract.

## Output contract

The endpoint returns the schema-versioned report used by Phase 2 feedback generation.

- `schema_version`
- `target`
- `language`
- `transcribed`
- `word_alignment`
- `fluency`
- `overall`

## Error behavior

- `400`: invalid audio payload or unsupported content.
- `503`: model dependency unavailable.
- `500`: unexpected analysis failure.
