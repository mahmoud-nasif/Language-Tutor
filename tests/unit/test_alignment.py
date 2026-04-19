from polyglot.analysis.alignment import align_phonemes


def test_alignment_exact_match() -> None:
    result = align_phonemes("theta r iy", "theta r iy")
    assert result.operations == ["match", "match", "match"]
    assert result.score > 0


def test_alignment_prefers_similar_substitution_cost() -> None:
    similar = align_phonemes("theta", "t")
    distant = align_phonemes("theta", "k")
    assert similar.score > distant.score


def test_alignment_handles_insert_delete() -> None:
    result = align_phonemes("r o t e", "r o")
    assert "delete" in result.operations
    assert result.expected_aligned[0] == "r"
