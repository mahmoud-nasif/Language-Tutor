import numpy as np

from polyglot.analysis.audio import _resample_bandlimited


def _sine(freq_hz: float, sample_rate: int, duration_s: float) -> np.ndarray:
    t = np.arange(int(sample_rate * duration_s), dtype=np.float32) / sample_rate
    return np.sin(2.0 * np.pi * freq_hz * t).astype(np.float32)


def _rms(signal: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(signal))))


def test_resample_suppresses_out_of_band_tone() -> None:
    # 10 kHz is above the 8 kHz Nyquist at 16 kHz and should be strongly attenuated.
    source = _sine(freq_hz=10_000.0, sample_rate=48_000, duration_s=1.0)
    resampled = _resample_bandlimited(source, from_rate=48_000, to_rate=16_000)

    attenuation_ratio = _rms(resampled) / max(_rms(source), 1e-12)
    assert attenuation_ratio < 0.15


def test_resample_preserves_in_band_tone_without_strong_spurs() -> None:
    source = _sine(freq_hz=3_000.0, sample_rate=48_000, duration_s=1.0)
    resampled = _resample_bandlimited(source, from_rate=48_000, to_rate=16_000)

    window = np.hanning(len(resampled))
    spectrum = np.abs(np.fft.rfft(resampled * window))
    freqs = np.fft.rfftfreq(len(resampled), 1.0 / 16_000.0)

    fundamental_idx = int(np.argmin(np.abs(freqs - 3_000.0)))
    fundamental_mag = float(spectrum[fundamental_idx])

    off_band_mask = (freqs < 2_900.0) | (freqs > 3_100.0)
    max_spur = float(np.max(spectrum[off_band_mask]))

    assert fundamental_mag > 0.0
    assert max_spur / fundamental_mag < 0.35
