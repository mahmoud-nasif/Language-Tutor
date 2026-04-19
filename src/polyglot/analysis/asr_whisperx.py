"""WhisperX integration with faster-whisper backend."""

from polyglot.analysis.audio import AudioSample
from polyglot.analysis.errors import DependencyUnavailableError
from polyglot.analysis.models import ASRResult, ASRWord, LanguageCode

WHISPER_LANGUAGE_MAP: dict[LanguageCode, str] = {
    "en-US": "en",
    "de-DE": "de",
}


class WhisperXASRService:
    """ASR service backed by WhisperX with word-level timing."""

    def __init__(self, model_name: str = "small", device: str = "cuda") -> None:
        self._model_name = model_name
        self._device = device
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        try:
            import whisperx
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
            raise DependencyUnavailableError("whisperx is not installed.") from exc

        compute_type = "float16" if self._device != "cpu" else "int8"
        self._model = whisperx.load_model(
            self._model_name,
            self._device,
            compute_type=compute_type,
            asr_options={"word_timestamps": True},
        )
        return self._model

    def transcribe(self, audio: AudioSample, language: LanguageCode) -> ASRResult:
        """Run ASR and emit transcript plus normalized word timings."""
        model = self._ensure_model()
        transcription = model.transcribe(
            audio.pcm16khz_mono, language=WHISPER_LANGUAGE_MAP[language]
        )

        transcript_text = transcription.get("text", "").strip()
        words: list[ASRWord] = []

        for segment in transcription.get("segments", []):
            for word in segment.get("words", []):
                token = str(word.get("word", "")).strip()
                if not token:
                    continue
                start_ms = int(round(float(word.get("start", 0.0)) * 1000))
                end_ms = int(round(float(word.get("end", 0.0)) * 1000))
                confidence = float(word.get("score", segment.get("avg_logprob", 0.0)))
                words.append(
                    ASRWord(
                        word=token,
                        start_ms=max(0, start_ms),
                        end_ms=max(start_ms, end_ms),
                        confidence=confidence,
                    )
                )

        return ASRResult(text=transcript_text, words=words)
