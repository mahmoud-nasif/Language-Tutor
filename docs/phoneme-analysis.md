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

## Worked example (en-US, fixture-backed)

Fixture: `tests/fixtures/en/en_03_Phoneme_substitution.wav`

- Target sentence: `I have been living in Hamburg for three years.`
- WhisperX transcript: `I have been living in Hamburg for 3 years.`
- Expected canonical phonemes:
	`ai h a v b i n l i v i ng i n h a m b er g f o r theta r i j i r z`
- Recognized canonical phonemes:
	`ai h a v b i n l i v i ng i n h a m b er g f o r theta r i j i r z`

Alignment result:

- Score: `60.0`
- Operations: all `match`

Final report snapshot:

- `overall.word_error_rate = 0.1111`
- `overall.phoneme_error_rate = 0.0`
- `overall.intelligibility_score = 0.9333`

Interpretation:

- This recording does not currently exhibit a detectable phoneme mismatch at the phoneme layer.
- ASR only differs by numeric formatting (`three` vs `3`).

## Worked example (de-DE, fixture-backed)

Fixture: `tests/fixtures/de/de_04_umlaut.wav`

- Target sentence: `Ich möchte einen Käse bestellen.`
- WhisperX transcript: `Ich muss dir einen Kase bestellen.`
- Expected canonical phonemes:
	`i ich m oe ich t schwa ai n schwa n k e z schwa b schwa sh t e l schwa n`
- Recognized canonical phonemes:
	`i s m u sh t e r ai n i n k a t s schwa b i sh t e l schwa n t`

Alignment result:

- Score: `16.0`
- Representative operations:
	- `oe -> u` (substitute)
	- `ich -> sh` (substitute)
	- `e -> a` around `Käse` (substitute)
	- trailing insertion near sentence end

Final report snapshot:

- `overall.word_error_rate = 0.6`
- `overall.phoneme_error_rate = 0.4783`
- `overall.intelligibility_score = 0.4487`

Interpretation:

- Umlaut-related vowel mismatch (`Käse` vs `Kase`) is surfaced in phoneme alignment.
- Lexical substitutions (`möchte` -> `muss`, extra `dir`) are also visible in ASR-level alignment.

## Report linkage

Phoneme mismatches are attached to word alignment items when substitution is observed. The resulting structure feeds `overall.phoneme_error_rate` and per-word phoneme error details.
