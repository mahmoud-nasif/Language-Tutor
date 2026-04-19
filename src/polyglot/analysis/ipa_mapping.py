"""IPA conversion helpers and language-specific normalization."""

import re

from polyglot.analysis.models import LanguageCode

ESPEAK_TOKEN_TO_IPA: dict[str, str] = {
    "T": "theta",
    "D": "eth",
    "S": "sh",
    "Z": "zh",
    "N": "ng",
    "R": "r",
    "tS": "tsh",
    "dZ": "dzh",
    "@": "schwa",
    "I": "i",
    "IY": "i",
    "EH": "e",
    "AE": "a",
    "AH": "a",
    "AA": "a",
    "AO": "o",
    "OW": "o",
    "UH": "u",
    "UW": "u",
}

GERMAN_MODEL_TOKEN_TO_IPA: dict[str, str] = {
    "R": "r",
    "j": "j",
    "v": "v",
    "w": "v",
    "z": "ts",
    "S": "sh",
    "C": "ich",
    "x": "ach",
    "2": "oe",
    "9": "oe",
    "Y": "ue",
    "y": "ue",
    "@": "schwa",
}

IPA_TO_CANONICAL: dict[str, str] = {
    "θ": "theta",
    "ð": "eth",
    "ʃ": "sh",
    "ʒ": "zh",
    "ŋ": "ng",
    "ɹ": "r",
    "ʁ": "r",
    "ʀ": "r",
    "ɾ": "r",
    "ə": "schwa",
    "ɐ": "schwa",
    "ø": "oe",
    "œ": "oe",
    "ɛ": "e",
    "ɪ": "i",
    "ʊ": "u",
    "ɔ": "o",
    "ɑ": "a",
    "æ": "a",
    "y": "ue",
    "ʏ": "ue",
    "ç": "ich",
    "x": "ach",
}

_TOKEN_SPLIT_RE = re.compile(r"[\s|,;/]+")


def _split_tokens(raw_text: str) -> list[str]:
    return [token for token in _TOKEN_SPLIT_RE.split(raw_text.strip()) if token]


def _canonicalize_token(raw_token: str) -> str:
    token = raw_token.strip().lower()
    token = token.replace("ˈ", "").replace("ˌ", "").replace("ː", "")
    token = token.replace("ɡ", "g")

    # Diphthongs and affricates are normalized first as multi-character units.
    token = token.replace("aɪ", "ai")
    token = token.replace("aʊ", "au")
    token = token.replace("ɔʏ", "oi")
    token = token.replace("eɪ", "ei")
    token = token.replace("t͡ʃ", "tsh")
    token = token.replace("d͡ʒ", "dzh")

    for source, target in IPA_TO_CANONICAL.items():
        token = token.replace(source, target)
    return token


def canonicalize_expected_ipa(ipa_text: str, language: LanguageCode) -> str:
    """Normalize phonemizer IPA output into canonical alignment tokens."""
    del language
    tokens = [_canonicalize_token(token) for token in _split_tokens(ipa_text)]
    return " ".join(token for token in tokens if token)


def canonicalize_recognized_phonemes(raw_text: str, language: LanguageCode) -> str:
    """Normalize wav2vec2 phoneme output into canonical alignment tokens."""
    tokens = _split_tokens(raw_text)
    canonical_tokens: list[str] = []

    if language == "en-US":
        for token in tokens:
            mapped = ESPEAK_TOKEN_TO_IPA.get(token, ESPEAK_TOKEN_TO_IPA.get(token.upper(), token))
            canonical_tokens.append(_canonicalize_token(mapped))
    else:
        for token in tokens:
            mapped = GERMAN_MODEL_TOKEN_TO_IPA.get(
                token, GERMAN_MODEL_TOKEN_TO_IPA.get(token.upper(), token)
            )
            canonical_tokens.append(_canonicalize_token(mapped))

    return " ".join(token for token in canonical_tokens if token)


def normalize_espeak_to_ipa(espeak_text: str) -> str:
    """Backward-compatible alias for canonicalizing recognizer output (en-US path)."""
    return canonicalize_recognized_phonemes(espeak_text, "en-US")


def normalize_german_to_ipa(raw_text: str) -> str:
    """Backward-compatible alias for canonicalizing recognizer output (de-DE path)."""
    return canonicalize_recognized_phonemes(raw_text, "de-DE")


def normalize_phoneme_output(raw_text: str, language: LanguageCode) -> str:
    """Backward-compatible API for recognizer canonicalization."""
    return canonicalize_recognized_phonemes(raw_text, language)
