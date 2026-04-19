"""IPA conversion helpers and language-specific normalization."""

from polyglot.analysis.models import LanguageCode

ESPEAK_TO_IPA: dict[str, str] = {
    "T": "theta",
    "D": "eth",
    "r": "r",
    "R": "r",
    "v": "v",
    "w": "w",
}

GERMAN_CHAR_TO_IPA: dict[str, str] = {
    "r": "r",
    "R": "r",
    "j": "j",
    "v": "f",
    "w": "v",
    "z": "ts",
    "sch": "sh",
}


def normalize_espeak_to_ipa(espeak_text: str) -> str:
    """Apply deterministic token-level substitutions to produce IPA-friendly output."""
    normalized = espeak_text
    for source, target in ESPEAK_TO_IPA.items():
        normalized = normalized.replace(source, target)
    return normalized.strip()


def normalize_german_to_ipa(raw_text: str) -> str:
    """Approximate German model output into IPA-like sequence using documented mapping."""
    normalized = raw_text
    for source, target in GERMAN_CHAR_TO_IPA.items():
        normalized = normalized.replace(source, target)
    return normalized.strip()


def normalize_phoneme_output(raw_text: str, language: LanguageCode) -> str:
    """Normalize model phoneme output per language."""
    if language == "de-DE":
        return normalize_german_to_ipa(raw_text)
    return normalize_espeak_to_ipa(raw_text)
