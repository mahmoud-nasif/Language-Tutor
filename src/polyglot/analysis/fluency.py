"""Fluency feature extraction from ASR timing metadata."""

import numpy as np

from polyglot.analysis.models import ASRWord, FluencyMetrics, LanguageCode

FILLERS_BY_LANGUAGE: dict[LanguageCode, set[str]] = {
    "en-US": {"um", "uh", "erm", "like"},
    "de-DE": {"aeh", "eh", "hm", "also"},
}


def _long_pauses_from_word_gaps(words: list[ASRWord], pause_threshold_ms: int) -> list[int]:
    long_pauses: list[int] = []
    for previous, current in zip(words, words[1:], strict=False):
        pause = current.start_ms - previous.end_ms
        if pause >= pause_threshold_ms:
            long_pauses.append(int(pause))
    return long_pauses


def _long_pauses_from_silero_vad(
    audio_pcm16khz_mono: np.ndarray,
    sample_rate: int,
    pause_threshold_ms: int,
) -> list[int]:
    if sample_rate <= 0 or audio_pcm16khz_mono.size == 0:
        return []

    try:
        from silero_vad import get_speech_timestamps, load_silero_vad
    except ModuleNotFoundError:
        return []

    try:
        model = load_silero_vad()
        speech_timestamps = get_speech_timestamps(
            audio_pcm16khz_mono,
            model,
            sampling_rate=sample_rate,
        )
    except Exception:
        return []

    long_pauses: list[int] = []
    for previous, current in zip(speech_timestamps, speech_timestamps[1:], strict=False):
        gap_samples = int(current["start"]) - int(previous["end"])
        gap_ms = int(round((gap_samples / sample_rate) * 1000))
        if gap_ms >= pause_threshold_ms:
            long_pauses.append(gap_ms)

    return long_pauses


def compute_fluency_metrics(
    words: list[ASRWord],
    duration_ms: int,
    language: LanguageCode,
    pause_threshold_ms: int = 700,
    audio_pcm16khz_mono: np.ndarray | None = None,
    sample_rate: int | None = None,
) -> FluencyMetrics:
    """Compute objective fluency metrics from word timings and transcript tokens."""
    if duration_ms <= 0:
        duration_ms = 1

    word_count = len(words)
    duration_minutes = duration_ms / 60000
    speech_rate = float(round(word_count / duration_minutes, 2)) if word_count else 0.0

    long_pauses = _long_pauses_from_word_gaps(words=words, pause_threshold_ms=pause_threshold_ms)
    if not long_pauses and audio_pcm16khz_mono is not None and sample_rate is not None:
        long_pauses = _long_pauses_from_silero_vad(
            audio_pcm16khz_mono=audio_pcm16khz_mono,
            sample_rate=sample_rate,
            pause_threshold_ms=pause_threshold_ms,
        )

    fillers = FILLERS_BY_LANGUAGE[language]
    filler_count = sum(1 for word in words if word.word.lower() in fillers)

    return FluencyMetrics(
        duration_ms=duration_ms,
        speech_rate_wpm=speech_rate,
        long_pauses_ms=long_pauses,
        filler_count=filler_count,
    )
