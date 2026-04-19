"""Audio preprocessing utilities for uploaded WAV clips."""

import io
from dataclasses import dataclass
from typing import cast

import numpy as np

from polyglot.analysis.errors import DependencyUnavailableError, InvalidAudioError

TARGET_SAMPLE_RATE = 16000


@dataclass(slots=True)
class AudioSample:
    """In-memory normalized mono signal at 16 kHz."""

    pcm16khz_mono: np.ndarray
    sample_rate: int
    duration_ms: int
    rms: float
    clipped: bool


def _resample_bandlimited(signal: np.ndarray, from_rate: int, to_rate: int) -> np.ndarray:
    """Resample with torchaudio sinc interpolation to avoid aliasing artifacts."""
    if from_rate == to_rate:
        return signal.astype(np.float32, copy=False)

    try:
        import torch
        from torchaudio.functional import resample
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
        raise DependencyUnavailableError(
            "torchaudio/torch dependencies are not installed."
        ) from exc

    waveform = torch.from_numpy(signal.astype(np.float32, copy=False)).unsqueeze(0)
    with torch.no_grad():
        resampled = resample(
            waveform,
            orig_freq=from_rate,
            new_freq=to_rate,
            lowpass_filter_width=64,
            rolloff=0.9475937167399596,
            resampling_method="sinc_interp_hann",
        )
    resampled_numpy = cast(np.ndarray, resampled.squeeze(0).cpu().numpy())
    return resampled_numpy.astype(np.float32, copy=False)


def preprocess_wav_bytes(
    wav_bytes: bytes,
    min_duration_ms: int = 300,
    max_duration_ms: int = 30000,
    silence_rms_threshold: float = 0.003,
) -> AudioSample:
    """Decode WAV bytes and normalize for model consumption."""
    if not wav_bytes:
        raise InvalidAudioError("Audio payload is empty.")

    try:
        import soundfile as sf

        signal, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="float32", always_2d=True)
    except Exception as exc:  # pragma: no cover - delegated to library exceptions
        raise InvalidAudioError("Unsupported or corrupted WAV payload.") from exc

    if signal.size == 0:
        raise InvalidAudioError("Audio payload has no samples.")

    mono = signal.mean(axis=1)
    mono = _resample_bandlimited(mono, sample_rate, TARGET_SAMPLE_RATE)

    peak = float(np.max(np.abs(mono)))
    clipped = peak >= 0.999
    if peak > 0:
        mono = (mono / peak) * 0.95

    rms = float(np.sqrt(np.mean(np.square(mono))))
    duration_ms = int(round(len(mono) / TARGET_SAMPLE_RATE * 1000))

    if duration_ms < min_duration_ms:
        raise InvalidAudioError("Audio is too short.")
    if duration_ms > max_duration_ms:
        raise InvalidAudioError("Audio is too long.")
    if rms < silence_rms_threshold:
        raise InvalidAudioError("Audio appears to be silence-only.")

    return AudioSample(
        pcm16khz_mono=mono.astype(np.float32),
        sample_rate=TARGET_SAMPLE_RATE,
        duration_ms=duration_ms,
        rms=rms,
        clipped=clipped,
    )
