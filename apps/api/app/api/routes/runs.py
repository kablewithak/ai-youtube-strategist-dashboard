from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.run import (
    AnalysisRun,
    AssumptionSet,
    CreateRunRequest,
    RunStatus,
    UpdateAssumptionsRequest,
)

router = APIRouter(prefix="/runs", tags=["runs"])

RUN_STORE: dict[UUID, AnalysisRun] = {}


def build_placeholder_assumptions(payload: CreateRunRequest) -> AssumptionSet:
    niche = payload.channel_niche.strip() or "the channel niche"

    return AssumptionSet(
        audience_interests=[
            "practical advice",
            "clear explanations",
            "content that feels immediately useful",
        ],
        likely_topic_patterns=[
            f"{niche} explainers",
            f"{niche} opinion or breakdown content",
        ],
        audience_intent=(
            "The audience likely wants relevant, actionable content that is easy to understand "
            "and directly connected to their interests."
        ),
        screenshot_interpretation="No screenshot analysis yet in scaffold mode.",
        confidence_notes=(
            "These are placeholder assumptions generated for plumbing validation. "
            "They are not final strategic conclusions."
        ),
    )


@router.post("", response_model=AnalysisRun)
def create_run(payload: CreateRunRequest) -> AnalysisRun:
    assumptions = build_placeholder_assumptions(payload)

    run = AnalysisRun(
        status=RunStatus.ASSUMPTIONS_DRAFTED,
        channel_url=payload.channel_url,
        channel_niche=payload.channel_niche,
        channel_goals=payload.channel_goals,
        audience_demographics=payload.audience_demographics,
        notes=payload.notes,
        assumptions=assumptions,
    )

    RUN_STORE[run.id] = run
    return run


@router.get("/{run_id}", response_model=AnalysisRun)
def get_run(run_id: UUID) -> AnalysisRun:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.patch("/{run_id}/assumptions", response_model=AnalysisRun)
def update_assumptions(run_id: UUID, payload: UpdateAssumptionsRequest) -> AnalysisRun:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    updated_run = run.model_copy(
        update={
            "status": RunStatus.ASSUMPTIONS_REVIEWED,
            "assumptions": payload.assumptions,
            "updated_at": datetime.utcnow(),
        }
    )

    RUN_STORE[run_id] = updated_run
    return updated_run