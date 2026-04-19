"""Application version helpers."""

from importlib.metadata import PackageNotFoundError, version

FALLBACK_VERSION = "0.1.0"


def get_app_version() -> str:
    """Return package version from metadata with a safe fallback for local runs."""
    try:
        return version("polyglot")
    except PackageNotFoundError:
        return FALLBACK_VERSION
