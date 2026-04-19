"""Fluency feature extraction from ASR timing metadata."""

from polyglot.analysis.models import ASRWord, FluencyMetrics, LanguageCode

FILLERS_BY_LANGUAGE: dict[LanguageCode, set[str]] = {
    "en-US": {"um", "uh", "erm", "like"},
    "de-DE": {"aeh", "eh", "hm", "also"},
}


def compute_fluency_metrics(
    words: list[ASRWord],
    duration_ms: int,
    language: LanguageCode,
    pause_threshold_ms: int = 700,
) -> FluencyMetrics:
    """Compute objective fluency metrics from word timings and transcript tokens."""
    if duration_ms <= 0:
        duration_ms = 1

    word_count = len(words)
    duration_minutes = duration_ms / 60000
    speech_rate = float(round(word_count / duration_minutes, 2)) if word_count else 0.0

    long_pauses: list[int] = []
    for previous, current in zip(words, words[1:], strict=False):
        pause = current.start_ms - previous.end_ms
        if pause >= pause_threshold_ms:
            long_pauses.append(int(pause))

    fillers = FILLERS_BY_LANGUAGE[language]
    filler_count = sum(1 for word in words if word.word.lower() in fillers)

    return FluencyMetrics(
        duration_ms=duration_ms,
        speech_rate_wpm=speech_rate,
        long_pauses_ms=long_pauses,
        filler_count=filler_count,
    )
