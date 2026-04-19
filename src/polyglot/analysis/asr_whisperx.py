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
        self._align_models: dict[str, tuple[object, dict]] = {}

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

    def _ensure_align_model(self, language: LanguageCode) -> tuple[object, dict]:
        language_code = WHISPER_LANGUAGE_MAP[language]
        if language_code in self._align_models:
            return self._align_models[language_code]

        try:
            import whisperx
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
            raise DependencyUnavailableError("whisperx is not installed.") from exc

        align_model, metadata = whisperx.load_align_model(
            language_code=language_code,
            device=self._device,
        )
        self._align_models[language_code] = (align_model, metadata)
        return align_model, metadata

    def _align_segments_with_words(
        self,
        segments: list[dict],
        audio: AudioSample,
        language: LanguageCode,
    ) -> list[dict]:
        if not segments:
            return segments

        try:
            import whisperx

            align_model, metadata = self._ensure_align_model(language)
            aligned = whisperx.align(
                transcript=segments,
                model=align_model,
                align_model_metadata=metadata,
                audio=audio.pcm16khz_mono,
                device=self._device,
                return_char_alignments=False,
            )
            aligned_segments = aligned.get("segments", segments)
            if isinstance(aligned_segments, list):
                return aligned_segments
        except Exception:
            # Alignment is a best-effort enhancement for timing quality.
            return segments

        return segments

    def transcribe(self, audio: AudioSample, language: LanguageCode) -> ASRResult:
        """Run ASR and emit transcript plus normalized word timings."""
        model = self._ensure_model()
        transcription = model.transcribe(
            audio.pcm16khz_mono, language=WHISPER_LANGUAGE_MAP[language]
        )
        segments = transcription.get("segments", [])
        if any(not segment.get("words") for segment in segments):
            segments = self._align_segments_with_words(segments, audio, language)
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
