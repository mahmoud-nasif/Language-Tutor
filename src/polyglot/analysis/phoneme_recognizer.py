"""wav2vec2-based phoneme recognition wrappers."""

from typing import Any

from polyglot.analysis.audio import AudioSample
from polyglot.analysis.errors import DependencyUnavailableError
from polyglot.analysis.ipa_mapping import canonicalize_recognized_phonemes
from polyglot.analysis.models import LanguageCode, PhonemeRecognitionResult

PHONEME_MODEL_ID = "facebook/wav2vec2-lv-60-espeak-cv-ft"


class Wav2Vec2PhonemeService:
    """Language-aware wav2vec2 phoneme recognizer."""

    def __init__(self, device: str = "cuda") -> None:
        self._device = device
        self._processor: Any = None
        self._model: Any = None

    def _ensure_model(self, language: LanguageCode) -> tuple[Any, Any]:
        del language
        if self._processor is not None and self._model is not None:
            return self._processor, self._model

        try:
            import torch
            from transformers import AutoModelForCTC, AutoProcessor
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
            raise DependencyUnavailableError(
                "transformers/torch dependencies are not installed."
            ) from exc

        processor = AutoProcessor.from_pretrained(PHONEME_MODEL_ID)
        model = AutoModelForCTC.from_pretrained(PHONEME_MODEL_ID)

        if self._device != "cpu" and torch.cuda.is_available():
            model = model.to("cuda")

        model.eval()
        self._processor = processor
        self._model = model
        return processor, model

    def recognize(self, audio: AudioSample, language: LanguageCode) -> PhonemeRecognitionResult:
        """Decode phoneme-like tokens and normalize them to IPA-compatible symbols."""
        processor, model = self._ensure_model(language)

        import torch

        inputs = processor(
            audio.pcm16khz_mono,
            sampling_rate=audio.sample_rate,
            return_tensors="pt",
            padding=True,
        )
        input_values = inputs.input_values
        attention_mask = getattr(inputs, "attention_mask", None)

        if self._device != "cpu" and torch.cuda.is_available():
            input_values = input_values.to("cuda")
            if attention_mask is not None:
                attention_mask = attention_mask.to("cuda")

        with torch.no_grad():
            logits = model(input_values, attention_mask=attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        raw_sequence = processor.batch_decode(predicted_ids)[0]
        normalized_sequence = canonicalize_recognized_phonemes(raw_sequence, language)

        confidence = float(torch.softmax(logits, dim=-1).max().item())
        return PhonemeRecognitionResult(
            espeak_sequence=str(raw_sequence).strip(),
            ipa_sequence=normalized_sequence,
            confidence=confidence,
        )


class MockPhonemeService:
    """Deterministic fallback service for testing and offline development."""

    def recognize(self, audio: AudioSample, language: LanguageCode) -> PhonemeRecognitionResult:
        del audio
        fallback = "theta r i" if language == "en-US" else "i x v o n e"
        return PhonemeRecognitionResult(
            espeak_sequence=fallback, ipa_sequence=fallback, confidence=0.0
        )
