"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from polyglot.api.routes.health import router as health_router
from polyglot.api.routes.metrics import router as metrics_router
from polyglot.api.version import get_app_version
from polyglot.config.settings import get_settings


def configure_logging(level: str) -> None:
    """Configure structured JSON logging for the service."""
    logging.basicConfig(format="%(message)s", level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Log startup and shutdown events."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = structlog.get_logger("polyglot")
    logger.info(
        "startup",
        app_env=settings.app_env,
        device=settings.device,
        llm_provider=settings.llm_provider,
        version=get_app_version(),
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""
    app = FastAPI(
        title="Polyglot",
        version=get_app_version(),
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(metrics_router)
    return app


app = create_app()
