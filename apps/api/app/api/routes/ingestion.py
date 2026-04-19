from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.routes.runs import RUN_STORE
from app.schemas.run import AnalysisRun, RunStatus
from app.services.evidence.summarizer import (
    build_assumptions_from_evidence,
    summarize_evidence,
)
from app.services.youtube.channel_resolver import resolve_youtube_channel
from app.services.youtube.comment_fetcher import fetch_comment_samples
from app.services.youtube.url_parser import parse_youtube_channel_url
from app.services.youtube.video_fetcher import fetch_recent_videos

router = APIRouter(prefix="/runs", tags=["ingestion"])


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/{run_id}/ingest-youtube", response_model=AnalysisRun)
def ingest_youtube_evidence(run_id: UUID) -> AnalysisRun:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        parsed_url = parse_youtube_channel_url(run.channel_url)
        channel = resolve_youtube_channel(parsed_url)
        videos = fetch_recent_videos(channel, limit=10)
        comment_samples = fetch_comment_samples(videos, per_video_limit=20)
        evidence_summary = summarize_evidence(videos, comment_samples)

        # Drafted assumptions are still computed for internal use,
        # but we do not overwrite the user's reviewed assumptions here.
        _ = build_assumptions_from_evidence(
            run.channel_niche,
            evidence_summary,
            videos,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"YouTube ingestion failed: {exc}",
        ) from exc

    updated_run = run.model_copy(
        update={
            "status": RunStatus.YOUTUBE_INGESTED,
            "youtube_channel": channel,
            "videos": videos,
            "comment_samples": comment_samples,
            "evidence_summary": evidence_summary,
            "updated_at": utc_now(),
        }
    )

    RUN_STORE[run_id] = updated_run
    return updated_run