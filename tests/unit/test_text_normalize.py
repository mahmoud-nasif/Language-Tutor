from polyglot.analysis.text_normalize import normalize_for_alignment


def test_normalize_for_alignment_expands_digits_in_english() -> None:
    text = "I have 3 years."

    assert normalize_for_alignment(text, "en-US") == "i have three years"


def test_normalize_for_alignment_expands_digits_in_german() -> None:
    text = "Ich habe 3 Jahre!"

    assert normalize_for_alignment(text, "de-DE") == "ich habe drei jahre"


def test_normalize_for_alignment_strips_punctuation_and_collapses_whitespace() -> None:
    text = "  Ich,   wohne...   in\nHamburg!  "

    assert normalize_for_alignment(text, "de-DE") == "ich wohne in hamburg"


def test_normalize_for_alignment_preserves_contractions() -> None:
    text = "I've been living here for 3 years."

    assert normalize_for_alignment(text, "en-US") == "i've been living here for three years"


def test_de03_expected_target_phrase_normalizes_to_reference_prefix() -> None:
    target = "Ich wohne seit drei Jahren in Hamburg."
    normalized = normalize_for_alignment(target, "de-DE")

    assert normalized.startswith("ich wohne seit")
