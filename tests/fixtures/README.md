## Real Recording Fixture Contract

This file is the authoritative contract for Phase 1 fixture verification.
If analyzer output disagrees with the `should_*` columns below, implementation is considered wrong.

### Suite Coverage

- Languages: English (`en-US`), German (`de-DE`)
- Cases: clean read, word substitution, phoneme substitution, long pause
- Additional German-specific gate: umlaut minimal-pair stress (`Kase` vs `Kaese` / `Käse`)

### Fixture Matrix (Authoritative)

| fixture_id | file | language | target_sentence | should_asr_behavior | should_phoneme_behavior | should_fluency_behavior |
| --- | --- | --- | --- | --- | --- | --- |
| en_01_clean | `tests/fixtures/en/en_01_clean.wav` | en-US | I have been living in Hamburg for three years. | Near-exact transcript | Near-zero phoneme errors | No long pauses |
| en_02_word_sub | `tests/fixtures/en/en_02_word_sub.wav` | en-US | I have been living in Hamburg for three years. | At least one lexical substitution should appear | Phoneme errors may occur around substituted token | No long pauses |
| en_03_phoneme_substitution | `tests/fixtures/en/en_03_Phoneme_substitution.wav` | en-US | I have been living in Hamburg for three years. | Transcript may remain semantically correct | Pronunciation error should be visible in phoneme alignment despite intelligible ASR | No long pauses |
| en_04_pause | `tests/fixtures/en/en_04_pause.wav` | en-US | I usually walk to work. | Transcript mostly correct | No major phoneme issue required | At least one long pause should be detected |
| en_05_contraction | `tests/fixtures/en/en_05_contaction.wav` | en-US | I've been living here for three years. | Transcript may normalize contraction form (`I've` vs `I have`) | Phoneme layer should remain mostly aligned | No long pauses |
| de_01_clean | `tests/fixtures/de/de_01_clean.wav` | de-DE | Ich wohne seit drei Jahren in Hamburg. | Near-exact transcript | Near-zero phoneme errors expected after German model fix | No long pauses |
| de_03_phoneme_sub | `tests/fixtures/de/de_03_phoneme_sub.wav` | de-DE | Rote Rosen. | Transcript may remain correct | Rhotic/fricative substitution should appear in phoneme alignment | No long pauses |
| de_04_word_sub | `tests/fixtures/de/de_04_word_sub.wav` | de-DE | Ich wohne seit drei Jahren in Hamburg. | At least one lexical substitution should appear | Phoneme mismatch should occur around substituted token | No long pauses |
| de_04_umlaut | `tests/fixtures/de/de_04_umlaut.wav` | de-DE | Ich möchte einen Käse bestellen. | Transcript may decompose umlaut (`Käse` -> `Kaese`/`Kase`) | Umlaut-related vowel mismatch should be detected | No long pauses |
| de_05_pause | `tests/fixtures/de/de_05_pause.wav` | de-DE | Heute lerne ich Deutsch. | Transcript mostly correct | No major phoneme issue required | At least one long pause should be detected |

### Notes

- File names reflect recording chronology and may not be sequential by case type.
- `de_04_word_sub.wav` is intentionally retained under its recorded filename.
- For reporting, use `fixture_id` above as the canonical label.
