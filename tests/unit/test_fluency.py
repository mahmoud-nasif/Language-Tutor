import numpy as np

from polyglot.analysis.fluency import compute_fluency_metrics
from polyglot.analysis.models import ASRWord


def _word(word: str, start_ms: int, end_ms: int) -> ASRWord:
    return ASRWord(word=word, start_ms=start_ms, end_ms=end_ms, confidence=1.0)


def test_long_pause_detection_from_word_timestamps() -> None:
    words = [
        _word("ich", 0, 200),
        _word("wohne", 220, 500),
        _word("seit", 1400, 1600),  # 900ms gap from previous word.
        _word("drei", 1620, 1800),
    ]

    metrics = compute_fluency_metrics(
        words=words,
        duration_ms=2500,
        language="de-DE",
        pause_threshold_ms=700,
    )

    assert metrics.long_pauses_ms == [900]


def test_no_long_pauses_when_gaps_below_threshold() -> None:
    words = [
        _word("i", 0, 100),
        _word("have", 200, 350),
        _word("been", 430, 520),
    ]

    metrics = compute_fluency_metrics(
        words=words,
        duration_ms=1500,
        language="en-US",
        pause_threshold_ms=700,
    )

    assert metrics.long_pauses_ms == []


def test_vad_fallback_populates_pause_when_word_gaps_are_flat(monkeypatch) -> None:
    words = [
        _word("ich", 900, 1200),
        _word("wohne", 1260, 1650),
        _word("seit", 1690, 1990),
        _word("drei", 2030, 2370),
        _word("jahren", 2410, 4180),
        _word("in", 4240, 4360),
    ]

    def fake_vad(*, audio_pcm16khz_mono, sample_rate, pause_threshold_ms):
        assert sample_rate == 16000
        assert pause_threshold_ms == 700
        assert audio_pcm16khz_mono.size > 0
        return [1028]

    monkeypatch.setattr(
        "polyglot.analysis.fluency._long_pauses_from_silero_vad",
        fake_vad,
    )

    metrics = compute_fluency_metrics(
        words=words,
        duration_ms=5400,
        language="de-DE",
        pause_threshold_ms=700,
        audio_pcm16khz_mono=np.zeros(16000, dtype=np.float32),
        sample_rate=16000,
    )

    assert metrics.long_pauses_ms == [1028]


def test_word_gap_pause_has_priority_over_vad_fallback(monkeypatch) -> None:
    words = [
        _word("ich", 0, 200),
        _word("wohne", 220, 500),
        _word("seit", 1400, 1600),
    ]

    def fail_vad(**_):
        raise AssertionError("VAD fallback should not run when word-gap pause already exists")

    monkeypatch.setattr(
        "polyglot.analysis.fluency._long_pauses_from_silero_vad",
        fail_vad,
    )

    metrics = compute_fluency_metrics(
        words=words,
        duration_ms=2500,
        language="de-DE",
        pause_threshold_ms=700,
        audio_pcm16khz_mono=np.zeros(16000, dtype=np.float32),
        sample_rate=16000,
    )

    assert metrics.long_pauses_ms == [900]
