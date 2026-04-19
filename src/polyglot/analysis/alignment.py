"""Needleman-Wunsch sequence alignment for phoneme analysis."""

from dataclasses import dataclass

DEFAULT_MATCH_SCORE = 2.0
DEFAULT_MISMATCH_SCORE = -1.0
DEFAULT_GAP_SCORE = -2.0

SIMILAR_PHONEME_COSTS: dict[tuple[str, str], float] = {
    ("theta", "t"): -0.25,
    ("t", "theta"): -0.25,
    ("v", "w"): -0.35,
    ("w", "v"): -0.35,
    ("r", "R"): -0.2,
    ("R", "r"): -0.2,
}


@dataclass(slots=True)
class AlignmentResult:
    """Aligned sequences and edit operations from Needleman-Wunsch."""

    expected_aligned: list[str]
    actual_aligned: list[str]
    operations: list[str]
    score: float


def _tokenize(sequence: str) -> list[str]:
    return [token for token in sequence.split() if token]


def _substitution_cost(expected: str, actual: str) -> float:
    if expected == actual:
        return DEFAULT_MATCH_SCORE
    return SIMILAR_PHONEME_COSTS.get((expected, actual), DEFAULT_MISMATCH_SCORE)


def align_phonemes(expected_sequence: str, actual_sequence: str) -> AlignmentResult:
    """Align expected and actual phoneme tokens with explicit scoring rules."""
    expected = _tokenize(expected_sequence)
    actual = _tokenize(actual_sequence)

    rows = len(expected) + 1
    cols = len(actual) + 1
    score_matrix = [[0.0 for _ in range(cols)] for _ in range(rows)]
    trace_matrix = [["" for _ in range(cols)] for _ in range(rows)]

    for i in range(1, rows):
        score_matrix[i][0] = score_matrix[i - 1][0] + DEFAULT_GAP_SCORE
        trace_matrix[i][0] = "up"
    for j in range(1, cols):
        score_matrix[0][j] = score_matrix[0][j - 1] + DEFAULT_GAP_SCORE
        trace_matrix[0][j] = "left"

    for i in range(1, rows):
        for j in range(1, cols):
            diag_score = score_matrix[i - 1][j - 1] + _substitution_cost(
                expected[i - 1], actual[j - 1]
            )
            up_score = score_matrix[i - 1][j] + DEFAULT_GAP_SCORE
            left_score = score_matrix[i][j - 1] + DEFAULT_GAP_SCORE

            best_score = max(diag_score, up_score, left_score)
            score_matrix[i][j] = best_score
            if best_score == diag_score:
                trace_matrix[i][j] = "diag"
            elif best_score == up_score:
                trace_matrix[i][j] = "up"
            else:
                trace_matrix[i][j] = "left"

    i = len(expected)
    j = len(actual)
    aligned_expected: list[str] = []
    aligned_actual: list[str] = []
    operations: list[str] = []

    while i > 0 or j > 0:
        step = trace_matrix[i][j] if i >= 0 and j >= 0 else ""
        if step == "diag":
            expected_token = expected[i - 1]
            actual_token = actual[j - 1]
            aligned_expected.append(expected_token)
            aligned_actual.append(actual_token)
            operations.append("match" if expected_token == actual_token else "substitute")
            i -= 1
            j -= 1
        elif step == "up":
            aligned_expected.append(expected[i - 1])
            aligned_actual.append("-")
            operations.append("delete")
            i -= 1
        else:
            aligned_expected.append("-")
            aligned_actual.append(actual[j - 1])
            operations.append("insert")
            j -= 1

    aligned_expected.reverse()
    aligned_actual.reverse()
    operations.reverse()

    return AlignmentResult(
        expected_aligned=aligned_expected,
        actual_aligned=aligned_actual,
        operations=operations,
        score=score_matrix[-1][-1],
    )
