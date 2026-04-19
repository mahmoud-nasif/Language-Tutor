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
