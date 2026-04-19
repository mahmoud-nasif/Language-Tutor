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
        segments = transcription.get("segments", [])
        transcript_text = str(transcription.get("text", "")).strip()
        if not transcript_text:
            # whisperx 3.x may only return segment-level text from the ASR pass.
            transcript_text = " ".join(
                str(segment.get("text", "")).strip()
                for segment in segments
                if str(segment.get("text", "")).strip()
            ).strip()

        words: list[ASRWord] = []

        for segment in segments:
            segment_words = segment.get("words", [])
            if segment_words:
                for word in segment_words:
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
                continue

            segment_text = str(segment.get("text", "")).strip()
            if not segment_text:
                continue
            tokens = [token for token in segment_text.split() if token]
            if not tokens:
                continue
            start_ms = int(round(float(segment.get("start", 0.0)) * 1000))
            end_ms = int(round(float(segment.get("end", 0.0)) * 1000))
            span_ms = max(1, end_ms - start_ms)
            step_ms = max(1, span_ms // len(tokens))

            # Fallback timing approximation when align model is not active.
            for idx, token in enumerate(tokens):
                token_start = start_ms + idx * step_ms
                token_end = end_ms if idx == len(tokens) - 1 else token_start + step_ms
                words.append(
                    ASRWord(
                        word=token,
                        start_ms=max(0, token_start),
                        end_ms=max(token_start, token_end),
                        confidence=float(segment.get("avg_logprob", 0.0)),
                    )
                )

        return ASRResult(text=transcript_text, words=words)
