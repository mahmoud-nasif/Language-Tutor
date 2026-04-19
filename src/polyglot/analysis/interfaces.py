"""Interfaces for model-backed analysis components."""

from typing import Protocol

from polyglot.analysis.audio import AudioSample
from polyglot.analysis.models import ASRResult, G2PResult, LanguageCode, PhonemeRecognitionResult


class ASRService(Protocol):
    """Speech-to-text service contract with word-level timing."""

    def transcribe(self, audio: "AudioSample", language: LanguageCode) -> ASRResult:
        """Return transcript and per-word timings for the clip."""


class PhonemeService(Protocol):
    """Phoneme recognition service contract."""

    def recognize(self, audio: "AudioSample", language: LanguageCode) -> PhonemeRecognitionResult:
        """Return phoneme sequence in espeak and IPA forms."""


class G2PService(Protocol):
    """Grapheme-to-phoneme service contract for target text."""

    def convert(self, sentence: str, language: LanguageCode) -> G2PResult:
        """Convert sentence text to IPA by token."""
