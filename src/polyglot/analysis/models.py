"""Typed models for the Phase 1 analysis contract."""

from typing import Literal

from pydantic import BaseModel, Field

LanguageCode = Literal["en-US", "de-DE"]


class PhonemeError(BaseModel):
    """Single phoneme-level mismatch."""

    expected: str
    got: str
    category: str


class WordAlignmentItem(BaseModel):
    """Word-level alignment entry with optional phoneme details."""

    expected: str
    got: str
    type: str
    start_ms: int = 0
    end_ms: int = 0
    expected_ipa: str | None = None
    actual_ipa: str | None = None
    phoneme_errors: list[PhonemeError] = Field(default_factory=list)


class FluencyMetrics(BaseModel):
    """Fluency-related features extracted from timing."""

    duration_ms: int
    speech_rate_wpm: float
    long_pauses_ms: list[int] = Field(default_factory=list)
    filler_count: int = 0


class OverallScores(BaseModel):
    """Overall objective scores derived from deterministic metrics."""

    word_error_rate: float
    phoneme_error_rate: float
    intelligibility_score: float


class AnalysisReport(BaseModel):
    """Structured error report consumed by the feedback layer."""

    schema_version: int = 1
    target: str
    language: LanguageCode
    transcribed: str
    word_alignment: list[WordAlignmentItem]
    fluency: FluencyMetrics
    overall: OverallScores


class ASRWord(BaseModel):
    """Word timing and confidence from ASR output."""

    word: str
    start_ms: int
    end_ms: int
    confidence: float


class ASRResult(BaseModel):
    """ASR transcript and word timing metadata."""

    text: str
    words: list[ASRWord]


class PhonemeRecognitionResult(BaseModel):
    """Phoneme model output before and after normalization."""

    espeak_sequence: str
    ipa_sequence: str
    confidence: float


class G2PWordResult(BaseModel):
    """G2P result for one lexical token."""

    word: str
    ipa: str


class G2PResult(BaseModel):
    """G2P output for full sentence."""

    sentence: str
    words: list[G2PWordResult]

    @property
    def joined_ipa(self) -> str:
        return " ".join(entry.ipa for entry in self.words)
