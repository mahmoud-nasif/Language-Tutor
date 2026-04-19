"""Health endpoint."""

from fastapi import APIRouter

from polyglot.api.version import get_app_version

router = APIRouter()


@router.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    """Report application readiness status."""
    return {"status": "ok", "version": get_app_version()}
