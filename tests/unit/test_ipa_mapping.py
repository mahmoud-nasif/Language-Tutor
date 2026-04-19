from polyglot.analysis.ipa_mapping import (
    canonicalize_expected_ipa,
    canonicalize_recognized_phonemes,
)


def test_english_expected_and_recognized_canonicalize_to_same_alphabet() -> None:
    expected = canonicalize_expected_ipa("θ ɹ iː", "en-US")
    recognized = canonicalize_recognized_phonemes("T R IY", "en-US")

    assert expected == "theta r i"
    assert recognized == "theta r i"


def test_german_expected_and_recognized_canonicalize_to_same_alphabet() -> None:
    expected = canonicalize_expected_ipa("m ø ç t ə", "de-DE")
    recognized = canonicalize_recognized_phonemes("m 2 C t @", "de-DE")

    assert expected == "m oe ich t schwa"
    assert recognized == "m oe ich t schwa"


def test_recognized_maps_strut_symbol_without_fallback_unknown() -> None:
    recognized = canonicalize_recognized_phonemes("ʌ", "en-US")

    assert recognized == "a"
    assert "?" not in recognized


def test_expected_drops_unknown_placeholder_tokens() -> None:
    expected = canonicalize_expected_ipa("hˈamb??k", "de-DE", source_word="Hamburg")

    assert "?" not in expected
    assert expected == "h a m b k"
