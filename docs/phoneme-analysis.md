# Phoneme Analysis

Phase 1 uses deterministic phoneme alignment to detect pronunciation issues before any LLM explanation step.

## Components

1. Expected phoneme sequence
	- Generated from `target_sentence` using `phonemizer` with `espeak-ng` backend.
	- Output is tokenized IPA-like sequence per word.
2. Actual phoneme sequence
	- Generated from wav2vec2 language model output.
	- Normalized into IPA-compatible symbols via explicit mapping rules.
3. Sequence alignment
	- Needleman-Wunsch over tokenized phoneme sequences.
	- Produces aligned expected/actual streams and operation tags.

## Scoring matrix

- Match: `+2.0`
- Mismatch: `-1.0`
- Gap (insert/delete): `-2.0`

Similarity-aware substitutions reduce penalty for known confusions:

- `theta <-> t`: `-0.25`
- `v <-> w`: `-0.35`
- `r <-> R`: `-0.20`

These values are intentionally explicit and version-controlled in code.

## Worked example (en-US)

Target: `three`

- Expected IPA: `theta r iy`
- Actual IPA: `t r iy`

Alignment result:

- `theta -> t` (substitute)
- `r -> r` (match)
- `iy -> iy` (match)

Outcome:

- Word can still be transcribed correctly by ASR.
- Phoneme layer captures `dental_fricative_stopping`.

## Worked example (de-DE)

Target: `Rote`

- Expected IPA: `r o t e`
- Actual IPA: `R o t e`

Alignment result:

- `r -> R` (low-cost substitute)
- Remaining phonemes match

Outcome:

- Captures rhotic variant without treating it as severe mismatch.

## Report linkage

Phoneme mismatches are attached to word alignment items when substitution is observed. The resulting structure feeds `overall.phoneme_error_rate` and per-word phoneme error details.
