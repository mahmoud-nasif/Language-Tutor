"""Orchestrates the deterministic Phase 1 analysis pipeline."""

from polyglot.analysis.aggregator import build_report
from polyglot.analysis.alignment import align_phonemes
from polyglot.analysis.asr_whisperx import WhisperXASRService
from polyglot.analysis.audio import preprocess_wav_bytes
from polyglot.analysis.fluency import compute_fluency_metrics
from polyglot.analysis.g2p import PhonemizerG2PService
from polyglot.analysis.interfaces import ASRService, G2PService, PhonemeService
from polyglot.analysis.models import AnalysisReport, LanguageCode
from polyglot.analysis.phoneme_recognizer import Wav2Vec2PhonemeService
from polyglot.config.settings import Settings


class AnalysisPipeline:
    """Main entry point for `/analyze` deterministic processing."""

    def __init__(
        self,
        asr_service: ASRService,
        phoneme_service: PhonemeService,
        g2p_service: G2PService,
        min_audio_ms: int = 300,
        max_audio_ms: int = 30000,
    ) -> None:
        self._asr_service = asr_service
        self._phoneme_service = phoneme_service
        self._g2p_service = g2p_service
        self._min_audio_ms = min_audio_ms
        self._max_audio_ms = max_audio_ms

    def analyze(
        self,
        audio_bytes: bytes,
        target_sentence: str,
        language: LanguageCode,
        pause_threshold_ms: int,
    ) -> AnalysisReport:
        """Run preprocessing, ASR, phoneme recognition, alignment, and aggregation."""
        audio = preprocess_wav_bytes(
            audio_bytes,
            min_duration_ms=self._min_audio_ms,
            max_duration_ms=self._max_audio_ms,
        )
        asr_result = self._asr_service.transcribe(audio=audio, language=language)
        phoneme_result = self._phoneme_service.recognize(audio=audio, language=language)

        target_g2p = self._g2p_service.convert(sentence=target_sentence, language=language)
        transcript_g2p = self._g2p_service.convert(sentence=asr_result.text, language=language)

        phoneme_alignment = align_phonemes(
            expected_sequence=target_g2p.joined_ipa,
            actual_sequence=phoneme_result.ipa_sequence,
        )

        fluency = compute_fluency_metrics(
            words=asr_result.words,
            duration_ms=audio.duration_ms,
            language=language,
            pause_threshold_ms=pause_threshold_ms,
        )

        return build_report(
            target_sentence=target_sentence,
            language=language,
            asr_result=asr_result,
            target_g2p=target_g2p,
            transcript_g2p=transcript_g2p,
            phoneme_alignment=phoneme_alignment,
            fluency=fluency,
        )


def build_default_pipeline(settings: Settings) -> AnalysisPipeline:
    """Create production pipeline wired to configured model services."""
    return AnalysisPipeline(
        asr_service=WhisperXASRService(model_name=settings.whisper_model, device=settings.device),
        phoneme_service=Wav2Vec2PhonemeService(device=settings.device),
        g2p_service=PhonemizerG2PService(),
        min_audio_ms=settings.min_audio_ms,
        max_audio_ms=settings.max_audio_ms,
    )
