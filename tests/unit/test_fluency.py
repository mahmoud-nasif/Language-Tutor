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
