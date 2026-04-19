from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.routes.runs import RUN_STORE
from app.schemas.run import AnalysisRun, RunStatus
from app.services.evidence.gemini_synthesizer import synthesize_run_evidence

router = APIRouter(prefix="/runs", tags=["synthesis"])


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/{run_id}/synthesize-evidence", response_model=AnalysisRun)
def synthesize_evidence(run_id: UUID) -> AnalysisRun:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.youtube_channel and not run.screenshots and not run.notes.strip():
        raise HTTPException(
            status_code=400,
            detail="There is not enough evidence yet. Add notes, screenshots, or ingest YouTube evidence first.",
        )

    try:
        synthesized_evidence = synthesize_run_evidence(run)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evidence synthesis failed: {exc}") from exc

    updated_run = run.model_copy(
        update={
            "status": RunStatus.EVIDENCE_SYNTHESIZED,
            "synthesized_evidence": synthesized_evidence,
            "updated_at": utc_now(),
        }
    )

    RUN_STORE[run_id] = updated_run
    return updated_run