"""Deterministic aggregation from model outputs to report schema."""

from difflib import SequenceMatcher

from polyglot.analysis.alignment import AlignmentResult
from polyglot.analysis.models import (
    AnalysisReport,
    ASRResult,
    FluencyMetrics,
    G2PResult,
    LanguageCode,
    OverallScores,
    PhonemeError,
    WordAlignmentItem,
)


def _word_alignment_items(
    target: str,
    transcribed: str,
    asr_result: ASRResult,
    target_g2p: G2PResult,
    transcript_g2p: G2PResult,
) -> list[WordAlignmentItem]:
    expected_words = [token for token in target.split() if token]
    actual_words = [token for token in transcribed.split() if token]

    expected_ipa_map = {item.word: item.ipa for item in target_g2p.words}
    actual_ipa_map = {item.word: item.ipa for item in transcript_g2p.words}

    matcher = SequenceMatcher(a=expected_words, b=actual_words)
    items: list[WordAlignmentItem] = []
    actual_word_cursor = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                expected_word = expected_words[i1 + offset]
                actual_word = actual_words[j1 + offset]
                timing = (
                    asr_result.words[actual_word_cursor]
                    if actual_word_cursor < len(asr_result.words)
                    else None
                )
                actual_word_cursor += 1
                items.append(
                    WordAlignmentItem(
                        expected=expected_word,
                        got=actual_word,
                        type="match",
                        start_ms=timing.start_ms if timing else 0,
                        end_ms=timing.end_ms if timing else 0,
                    )
                )
        elif tag == "replace":
            replace_count = max(i2 - i1, j2 - j1)
            for offset in range(replace_count):
                expected_word = expected_words[i1 + offset] if i1 + offset < i2 else ""
                actual_word = actual_words[j1 + offset] if j1 + offset < j2 else ""
                timing = (
                    asr_result.words[actual_word_cursor]
                    if actual_word_cursor < len(asr_result.words)
                    else None
                )
                if actual_word:
                    actual_word_cursor += 1

                expected_ipa = expected_ipa_map.get(expected_word, "")
                actual_ipa = actual_ipa_map.get(actual_word, "")
                phoneme_errors: list[PhonemeError] = []
                if expected_ipa and actual_ipa and expected_ipa != actual_ipa:
                    phoneme_errors.append(
                        PhonemeError(
                            expected=expected_ipa.split()[0]
                            if expected_ipa.split()
                            else expected_ipa,
                            got=actual_ipa.split()[0] if actual_ipa.split() else actual_ipa,
                            category="substitution",
                        )
                    )

                items.append(
                    WordAlignmentItem(
                        expected=expected_word,
                        got=actual_word,
                        type="substitution",
                        start_ms=timing.start_ms if timing else 0,
                        end_ms=timing.end_ms if timing else 0,
                        expected_ipa=expected_ipa or None,
                        actual_ipa=actual_ipa or None,
                        phoneme_errors=phoneme_errors,
                    )
                )
        elif tag == "delete":
            for offset in range(i2 - i1):
                expected_word = expected_words[i1 + offset]
                items.append(WordAlignmentItem(expected=expected_word, got="", type="omission"))
        elif tag == "insert":
            for offset in range(j2 - j1):
                actual_word = actual_words[j1 + offset]
                timing = (
                    asr_result.words[actual_word_cursor]
                    if actual_word_cursor < len(asr_result.words)
                    else None
                )
                actual_word_cursor += 1
                items.append(
                    WordAlignmentItem(
                        expected="",
                        got=actual_word,
                        type="insertion",
                        start_ms=timing.start_ms if timing else 0,
                        end_ms=timing.end_ms if timing else 0,
                    )
                )

    return items


def _overall_scores(
    word_alignment: list[WordAlignmentItem], phoneme_alignment: AlignmentResult
) -> OverallScores:
    total_words = max(1, len([item for item in word_alignment if item.expected]))
    word_errors = len([item for item in word_alignment if item.type != "match"])
    word_error_rate = round(word_errors / total_words, 4)

    total_phonemes = max(
        1, len([token for token in phoneme_alignment.expected_aligned if token != "-"])
    )
    phoneme_errors = len([op for op in phoneme_alignment.operations if op != "match"])
    phoneme_error_rate = round(phoneme_errors / total_phonemes, 4)

    intelligibility = max(
        0.0, min(1.0, round(1.0 - (word_error_rate * 0.6 + phoneme_error_rate * 0.4), 4))
    )

    return OverallScores(
        word_error_rate=word_error_rate,
        phoneme_error_rate=phoneme_error_rate,
        intelligibility_score=intelligibility,
    )


def build_report(
    target_sentence: str,
    language: LanguageCode,
    asr_result: ASRResult,
    target_g2p: G2PResult,
    transcript_g2p: G2PResult,
    phoneme_alignment: AlignmentResult,
    fluency: FluencyMetrics,
) -> AnalysisReport:
    """Build schema_version=1 report from deterministic intermediate outputs."""
    word_alignment = _word_alignment_items(
        target=target_sentence,
        transcribed=asr_result.text,
        asr_result=asr_result,
        target_g2p=target_g2p,
        transcript_g2p=transcript_g2p,
    )
    overall = _overall_scores(word_alignment=word_alignment, phoneme_alignment=phoneme_alignment)

    return AnalysisReport(
        target=target_sentence,
        language=language,
        transcribed=asr_result.text,
        word_alignment=word_alignment,
        fluency=fluency,
        overall=overall,
    )
