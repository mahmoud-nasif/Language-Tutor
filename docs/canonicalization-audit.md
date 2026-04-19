# Canonicalization Audit (Phase 1, Linux)

## Scope

This audit targets phoneme canonicalization gaps that inflate phoneme error rate (PER), with emphasis on symbols that fall through to unknown placeholders.

Audit goals:

- identify every unmapped symbol,
- quantify frequency and affected fixtures/words,
- apply explicit mappings/handling in canonicalization,
- verify no `?` tokens remain in expected canonical streams.

Inputs were taken from the authoritative fixture matrix in `tests/fixtures/README.md`.

## Method

1. Added audit instrumentation in `ipa_mapping.py` to record unmapped symbols with:
   - symbol + Unicode codepoint,
   - fixture id,
   - source word/token,
   - stream (`expected` or `recognized`),
   - raw token.
2. Ran full 10-fixture suite with instrumentation enabled and captured pre-fix raw events.
3. Applied canonicalization closure changes based on observed symbols.
4. Re-ran suite and verified expected canonical streams contain zero `?` tokens.

## Findings

### Pre-fix unmapped symbols

| Symbol | Codepoint | Frequency | Stream | Affected fixture(s) | Affected word/token | Raw token | Proposed handling |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| ʌ | U+028C | 1 | recognized | en_05_contraction | ʌ | ʌ | Map to canonical `a` |

### Placeholder audit after instrumentation closure

After enabling placeholder capture, upstream placeholder symbols were observed in expected-side phonemizer output:

| Symbol | Codepoint | Frequency | Stream | Affected fixture(s) | Affected word | Raw token | Proposed handling |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| ? | U+003F | 12 | expected | de_01_clean, de_03_phoneme_sub, de_04_word_sub, de_05_pause | Hamburg | hˈamb??k | Drop placeholder token from canonical output and keep it audited |

### Why this is not guesswork

- The `ʌ` mapping came directly from observed unmapped symbol events.
- The `?` placeholder is generated upstream by phonemizer output (`hˈamb??k`), not by local symbol substitution logic.
- The closure strategy for `?` was containment: keep explicit audit visibility while preventing placeholder tokens from entering alignment.

## Code changes made

1. Added explicit IPA mapping:
   - `ʌ -> a`
2. Added canonicalization audit APIs in `ipa_mapping.py`:
   - enable/disable,
   - fixture context,
   - event collection.
3. Added placeholder handling in canonicalization:
   - `?` is audited and omitted from canonical token stream.
4. Added punctuation sanitization before phonemizer in `g2p.py` tokenization.

## Test coverage added

New regression tests in `tests/unit/test_ipa_mapping.py`:

- `test_recognized_maps_strut_symbol_without_fallback_unknown`
- `test_expected_drops_unknown_placeholder_tokens`

## Verification results

- Expected canonical streams with `?` tokens (post-fix): **0**
- Canonicalization audit event symbols (post-fix): only placeholder `?` events from upstream `hˈamb??k` emission

### de_01_clean PER (before vs after Task 1)

- Before: `0.3846`
- After: `0.4167`

Interpretation:

- The unknown-token cleanup removed synthetic `?` tokens from expected streams (goal achieved).
- PER did not improve in this isolated step and slightly increased, indicating residual mismatch is dominated by alignment/metric behavior and/or upstream transcript/phoneme variance rather than unmapped-symbol inflation alone.

## de_03 Target Corruption Postmortem

The prior `de_03` run that showed target text like `Rote Rosen` was not caused by normalization or canonicalization mutating the target sentence.

Root cause: the run was fed by a stale legacy fixture target source (old golden/integration matrix), where the German phoneme-substitution case still used `Rote Rosen`. The authoritative fixture contract (`tests/fixtures/README.md`) defines `de_03` target as `Ich wohne seit drei Jahren in Hamburg.`

Action taken:

- Added a normalization guard test in commit `c2845f2` to protect the expected `de_03` prefix path.
- Continued all fixture diagnostics/runs against the authoritative README matrix.