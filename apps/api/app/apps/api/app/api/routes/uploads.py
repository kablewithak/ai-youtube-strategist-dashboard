from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.routes.runs import RUN_STORE
from app.schemas.run import AnalysisRun
from app.services.evidence.storage import save_screenshot_upload

router = APIRouter(prefix="/runs", tags=["uploads"])


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/{run_id}/screenshots", response_model=AnalysisRun)
async def upload_screenshots(
    run_id: UUID,
    files: list[UploadFile] = File(...),
) -> AnalysisRun:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if not files:
        raise HTTPException(status_code=400, detail="No screenshot files were provided.")

    saved = []

    try:
        for file in files:
            saved_item = await save_screenshot_upload(file)
            saved.append(saved_item)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save screenshot(s): {exc}") from exc

    updated_run = run.model_copy(
        update={
            "screenshots": [*run.screenshots, *saved],
            "updated_at": utc_now(),
        }
    )

    RUN_STORE[run_id] = updated_run
    return updated_run