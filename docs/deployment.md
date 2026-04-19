# Deployment

## Tested hosts

- Linux host with Docker Engine + nvidia-container-toolkit: primary development and deployment path.
- Windows 11 with Docker Desktop (WSL2 backend): supported secondary path.

## Expected support

- Linux with Docker Engine and nvidia-container-toolkit.
- macOS with docker-compose.cpu.yml override.

## Notes

- Default `docker-compose.yml` is GPU-first and recommended on Linux.
- Use `docker-compose.cpu.yml` for CPU-only hosts and quick local validation.
- The CPU compose variant supports live source mounts for rapid debugging.

## Recording fixtures (Linux)

Contributors can record WAV fixtures directly on Linux with ALSA tools.

Example capture command:

```bash
arecord -f S16_LE -r 16000 -c 1 tests/fixtures/en/new_fixture.wav
```

Recommended checks:

- Use mono, 16-bit PCM WAV.
- Keep filenames aligned with the fixture matrix in `tests/fixtures/README.md`.
- Verify playback locally (`aplay <file>`) before committing.

## Torch and CUDA compatibility (Phase 1)

- Base image: `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04`
- Python runtime: `3.11`
- Torch pin: `torch==2.4.1+cu124`
- Torchaudio pin: `torchaudio==2.4.1+cu124`
- Index: `https://download.pytorch.org/whl/cu124`

The project pins torch ecosystem packages exactly to reduce breakage from minor upstream wheel changes.
