"""Phase 1 headless analysis endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from polyglot.analysis.errors import AnalysisError, DependencyUnavailableError, InvalidAudioError
from polyglot.analysis.models import AnalysisReport, LanguageCode
from polyglot.analysis.pipeline import AnalysisPipeline
from polyglot.api.dependencies import get_analysis_pipeline
from polyglot.config.settings import get_settings

router = APIRouter()


@router.post("/analyze", response_model=AnalysisReport, tags=["analysis"])
async def analyze_audio(
    audio: Annotated[UploadFile, File(description="WAV audio clip")],
    target_sentence: Annotated[str, Form(min_length=1)],
    language: Annotated[LanguageCode, Form()],
    pipeline: Annotated[AnalysisPipeline, Depends(get_analysis_pipeline)],
) -> AnalysisReport:
    """Analyze uploaded WAV against target text and return structured report."""
    if audio.content_type not in {"audio/wav", "audio/x-wav", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only WAV uploads are supported in V1.")

    payload = await audio.read()
    settings = get_settings()

    try:
        return pipeline.analyze(
            audio_bytes=payload,
            target_sentence=target_sentence,
            language=language,
            pause_threshold_ms=settings.pause_threshold_ms,
        )
    except InvalidAudioError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DependencyUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AnalysisError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
