"""Domain-specific errors for the analysis pipeline."""


class AnalysisError(Exception):
    """Base exception for analysis failures."""


class InvalidAudioError(AnalysisError):
    """Raised when audio payload is invalid for analysis."""


class DependencyUnavailableError(AnalysisError):
    """Raised when optional model dependencies are unavailable."""
