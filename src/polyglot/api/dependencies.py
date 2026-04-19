"""Dependency providers for API routes."""

from functools import lru_cache

from polyglot.analysis.pipeline import AnalysisPipeline, build_default_pipeline
from polyglot.config.settings import get_settings


@lru_cache(maxsize=1)
def get_analysis_pipeline() -> AnalysisPipeline:
    """Return singleton analysis pipeline instance for request handlers."""
    return build_default_pipeline(get_settings())
