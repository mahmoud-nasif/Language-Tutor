# Analysis Module Signatures (Implemented)

This document records the current module-level and class method signatures in analysis components for:
- audio I/O
- WhisperX wrapper
- wav2vec2 wrapper
- G2P
- alignment
- aggregation

Status: extracted from the current implementation on 2026-04-19.

## src/polyglot/analysis/audio.py

Module constants
- TARGET_SAMPLE_RATE: int = 16000

Data structures
- @dataclass(slots=True)
  class AudioSample:
    - pcm16khz_mono: np.ndarray
    - sample_rate: int
    - duration_ms: int
    - rms: float
    - clipped: bool

Functions
- def _resample_linear(signal: np.ndarray, from_rate: int, to_rate: int) -> np.ndarray
- def preprocess_wav_bytes(
    wav_bytes: bytes,
    min_duration_ms: int = 300,
    max_duration_ms: int = 30000,
    silence_rms_threshold: float = 0.003,
  ) -> AudioSample

## src/polyglot/analysis/asr_whisperx.py

Module constants
- WHISPER_LANGUAGE_MAP: dict[LanguageCode, str]

Classes and methods
- class WhisperXASRService:
  - def __init__(self, model_name: str = "small", device: str = "cuda") -> None
  - def _ensure_model(self)
  - def transcribe(self, audio: AudioSample, language: LanguageCode) -> ASRResult

## src/polyglot/analysis/phoneme_recognizer.py

Module constants
- MODEL_BY_LANGUAGE: dict[LanguageCode, str]

Classes and methods
- class Wav2Vec2PhonemeService:
  - def __init__(self, device: str = "cuda") -> None
  - def _ensure_model(self, language: LanguageCode) -> tuple[Any, Any]
  - def recognize(self, audio: AudioSample, language: LanguageCode) -> PhonemeRecognitionResult

- class MockPhonemeService:
  - def recognize(self, audio: AudioSample, language: LanguageCode) -> PhonemeRecognitionResult

## src/polyglot/analysis/g2p.py

Module constants
- PHONEMIZER_LANGUAGE_MAP: dict[LanguageCode, str]

Classes and methods
- class PhonemizerG2PService:
  - def convert(self, sentence: str, language: LanguageCode) -> G2PResult

## src/polyglot/analysis/alignment.py

Module constants
- DEFAULT_MATCH_SCORE = 2.0
- DEFAULT_MISMATCH_SCORE = -1.0
- DEFAULT_GAP_SCORE = -2.0
- SIMILAR_PHONEME_COSTS: dict[tuple[str, str], float]

Data structures
- @dataclass(slots=True)
  class AlignmentResult:
    - expected_aligned: list[str]
    - actual_aligned: list[str]
    - operations: list[str]
    - score: float

Functions
- def _tokenize(sequence: str) -> list[str]
- def _substitution_cost(expected: str, actual: str) -> float
- def align_phonemes(expected_sequence: str, actual_sequence: str) -> AlignmentResult

## src/polyglot/analysis/aggregator.py

Functions
- def _word_alignment_items(
    target: str,
    transcribed: str,
    asr_result: ASRResult,
    target_g2p: G2PResult,
    transcript_g2p: G2PResult,
  ) -> list[WordAlignmentItem]

- def _overall_scores(
    word_alignment: list[WordAlignmentItem],
    phoneme_alignment: AlignmentResult,
  ) -> OverallScores

- def build_report(
    target_sentence: str,
    language: LanguageCode,
    asr_result: ASRResult,
    target_g2p: G2PResult,
    transcript_g2p: G2PResult,
    phoneme_alignment: AlignmentResult,
    fluency: FluencyMetrics,
  ) -> AnalysisReport

## Public Entry Points Summary

The primary externally useful entry points in this set are:
- preprocess_wav_bytes (audio normalization and validation)
- WhisperXASRService.transcribe (ASR)
- Wav2Vec2PhonemeService.recognize (phoneme recognition)
- PhonemizerG2PService.convert (G2P conversion)
- align_phonemes (sequence alignment)
- build_report (deterministic report assembly)
