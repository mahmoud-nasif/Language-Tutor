from polyglot.analysis.aggregator import _overall_scores
from polyglot.analysis.alignment import AlignmentResult
from polyglot.analysis.models import WordAlignmentItem


def _match_item(word: str) -> WordAlignmentItem:
    return WordAlignmentItem(expected=word, got=word, type="match")


def _sub_item(expected: str, got: str) -> WordAlignmentItem:
    return WordAlignmentItem(expected=expected, got=got, type="substitution")


def _ins_item(got: str) -> WordAlignmentItem:
    return WordAlignmentItem(expected="", got=got, type="insertion")


def test_overall_identical_sequences_yield_zero_wer_per() -> None:
    word_alignment = [_match_item("I"), _match_item("have"), _match_item("three")]
    phoneme_alignment = AlignmentResult(
        expected_aligned=["theta", "r", "i"],
        actual_aligned=["theta", "r", "i"],
        operations=["match", "match", "match"],
        score=6.0,
    )

    overall = _overall_scores(word_alignment, phoneme_alignment)

    assert overall.word_error_rate == 0.0
    assert overall.phoneme_error_rate == 0.0


def test_overall_word_error_rate_matches_substitution_ratio() -> None:
    # Two substitutions over five expected words -> WER = 2/5.
    word_alignment = [
        _sub_item("I", "You"),
        _match_item("have"),
        _sub_item("three", "free"),
        _match_item("years"),
        _match_item("today"),
    ]
    phoneme_alignment = AlignmentResult(
        expected_aligned=["a", "b"],
        actual_aligned=["a", "b"],
        operations=["match", "match"],
        score=4.0,
    )

    overall = _overall_scores(word_alignment, phoneme_alignment)

    assert overall.word_error_rate == 0.4


def test_overall_phoneme_error_rate_matches_substitution_ratio() -> None:
    # Three substitutions over six expected phonemes -> PER = 3/6.
    word_alignment = [_match_item("ok")]
    phoneme_alignment = AlignmentResult(
        expected_aligned=["a", "b", "c", "d", "e", "f"],
        actual_aligned=["a", "x", "c", "y", "e", "z"],
        operations=["match", "substitute", "match", "substitute", "match", "substitute"],
        score=0.0,
    )

    overall = _overall_scores(word_alignment, phoneme_alignment)

    assert overall.phoneme_error_rate == 0.5


def test_insertions_do_not_inflate_word_error_rate_above_substitution_ratio() -> None:
    # Insertions are not expected-side pronunciation errors and should not affect WER.
    word_alignment = [
        _match_item("I"),
        _match_item("usually"),
        _match_item("walk"),
        _ins_item("really"),
        _ins_item("quickly"),
    ]
    phoneme_alignment = AlignmentResult(
        expected_aligned=["a"],
        actual_aligned=["a"],
        operations=["match"],
        score=2.0,
    )

    overall = _overall_scores(word_alignment, phoneme_alignment)

    assert overall.word_error_rate == 0.0


def test_insertions_do_not_inflate_phoneme_error_rate() -> None:
    # PER should be substitution/deletion based over expected phonemes only.
    word_alignment = [_match_item("ok")]
    phoneme_alignment = AlignmentResult(
        expected_aligned=["a", "b", "c"],
        actual_aligned=["a", "x", "b", "y", "c"],
        operations=["match", "insert", "match", "insert", "match"],
        score=0.0,
    )

    overall = _overall_scores(word_alignment, phoneme_alignment)

    assert overall.phoneme_error_rate == 0.0
