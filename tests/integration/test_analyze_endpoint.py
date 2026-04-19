import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from polyglot.analysis.models import AnalysisReport
from polyglot.api.app import create_app
from polyglot.api.dependencies import get_analysis_pipeline

CASE_MATRIX = [
    (
        "tests/fixtures/en/en_clean_read.wav",
        "I've been living here for three years",
        "en-US",
        "tests/golden/en_clean_read.json",
    ),
    (
        "tests/fixtures/en/en_word_substitution.wav",
        "I've been living here for three years",
        "en-US",
        "tests/golden/en_word_substitution.json",
    ),
    (
        "tests/fixtures/en/en_phoneme_substitution.wav",
        "Think about this theory",
        "en-US",
        "tests/golden/en_phoneme_substitution.json",
    ),
    (
        "tests/fixtures/en/en_long_pause.wav",
        "I usually walk to work",
        "en-US",
        "tests/golden/en_long_pause.json",
    ),
    (
        "tests/fixtures/de/de_clean_read.wav",
        "Ich wohne in Hamburg",
        "de-DE",
        "tests/golden/de_clean_read.json",
    ),
    (
        "tests/fixtures/de/de_word_substitution.wav",
        "Ich wohne in Hamburg",
        "de-DE",
        "tests/golden/de_word_substitution.json",
    ),
    (
        "tests/fixtures/de/de_phoneme_substitution.wav",
        "Rote Rosen",
        "de-DE",
        "tests/golden/de_phoneme_substitution.json",
    ),
    (
        "tests/fixtures/de/de_long_pause.wav",
        "Heute lerne ich Deutsch",
        "de-DE",
        "tests/golden/de_long_pause.json",
    ),
]


class FakePipeline:
    def __init__(self, reports_by_key: dict[tuple[str, str, str], dict]):
        self._reports_by_key = reports_by_key

    def analyze(
        self, audio_bytes: bytes, target_sentence: str, language: str, pause_threshold_ms: int
    ) -> AnalysisReport:
        del pause_threshold_ms
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        payload = self._reports_by_key[(language, target_sentence, audio_hash)]
        return AnalysisReport.model_validate(payload)


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_analyze_endpoint_with_golden_reports() -> None:
    app = create_app()

    reports_by_key: dict[tuple[str, str, str], dict] = {}
    for fixture_path, target, language, golden_path in CASE_MATRIX:
        fixture_bytes = Path(fixture_path).read_bytes()
        fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
        reports_by_key[(language, target, fixture_hash)] = _load_json(golden_path)

    app.dependency_overrides[get_analysis_pipeline] = lambda: FakePipeline(reports_by_key)

    client = TestClient(app)

    for fixture_path, target, language, golden_path in CASE_MATRIX:
        payload = Path(fixture_path).read_bytes()
        response = client.post(
            "/analyze",
            data={"target_sentence": target, "language": language},
            files={"audio": (Path(fixture_path).name, payload, "audio/wav")},
        )
        assert response.status_code == 200
        assert response.json() == _load_json(golden_path)
