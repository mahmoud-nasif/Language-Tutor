"""Text normalization helpers for robust word-level alignment."""

import re

from num2words import num2words

from polyglot.analysis.models import LanguageCode

_DIGIT_RE = re.compile(r"\d+")
_WHITESPACE_RE = re.compile(r"\s+")


def _num2words_language(language: LanguageCode) -> str:
    return "en" if language == "en-US" else "de"


def _expand_digits(text: str, language: LanguageCode) -> str:
    lang = _num2words_language(language)

    def repl(match: re.Match[str]) -> str:
        value = int(match.group(0))
        return str(num2words(value, lang=lang))

    return _DIGIT_RE.sub(repl, text)


def normalize_for_alignment(text: str, language: LanguageCode) -> str:
    """Normalize transcript text for stable word-level comparison."""
    normalized = text.lower()
    normalized = _expand_digits(normalized, language)

    # Keep apostrophes for contractions while stripping punctuation.
    normalized = re.sub(r"[^\w\s'äöüß]", " ", normalized, flags=re.UNICODE)
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized
