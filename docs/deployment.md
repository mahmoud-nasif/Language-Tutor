# Deployment

## Tested hosts

- Windows 11 with Docker Desktop (WSL2 backend): validated in Phase 0.

## Expected support

- Linux with Docker Engine and nvidia-container-toolkit.
- macOS with docker-compose.cpu.yml override.

## Notes

- Default docker-compose.yml is GPU-first.
- Use docker-compose.cpu.yml for CPU-only hosts.
- Phase 1 will add torch plus ASR dependencies and increase image size.

## Torch and CUDA compatibility (Phase 1)

- Base image: `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04`
- Python runtime: `3.11`
- Torch pin: `torch==2.4.1+cu124`
- Torchaudio pin: `torchaudio==2.4.1+cu124`
- Index: `https://download.pytorch.org/whl/cu124`

The project pins torch ecosystem packages exactly to reduce breakage from minor upstream wheel changes.
