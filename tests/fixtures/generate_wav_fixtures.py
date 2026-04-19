import math
import os
import struct
import wave

sr = 16000
amp = 12000

files = {
    "tests/fixtures/en/en_clean_read.wav": [(440, 0.40), (660, 0.40), (550, 0.40)],
    "tests/fixtures/en/en_word_substitution.wav": [(440, 0.35), (880, 0.35), (550, 0.50)],
    "tests/fixtures/en/en_phoneme_substitution.wav": [
        (440, 0.30),
        (620, 0.30),
        (700, 0.30),
        (550, 0.35),
    ],
    "tests/fixtures/en/en_long_pause.wav": [(440, 0.35), (None, 0.75), (550, 0.45)],
    "tests/fixtures/de/de_clean_read.wav": [(392, 0.40), (587, 0.40), (494, 0.40)],
    "tests/fixtures/de/de_word_substitution.wav": [(392, 0.35), (784, 0.35), (494, 0.50)],
    "tests/fixtures/de/de_phoneme_substitution.wav": [
        (392, 0.30),
        (554, 0.30),
        (659, 0.30),
        (494, 0.35),
    ],
    "tests/fixtures/de/de_long_pause.wav": [(392, 0.35), (None, 0.80), (494, 0.45)],
}

for path, segments in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    samples = []
    phase = 0.0
    for freq, dur in segments:
        n = int(sr * dur)
        if freq is None:
            samples.extend([0] * n)
        else:
            step = 2.0 * math.pi * freq / sr
            for _ in range(n):
                samples.append(int(amp * math.sin(phase)))
                phase += step
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))
