from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.routes.runs import RUN_STORE
from app.schemas.recommendations import RecommendationDraftResponse
from app.services.analysis.audience_psychology import analyze_audience_psychology
from app.services.recommendations.candidate_generator import generate_candidate_ideas
from app.services.recommendations.packager import create_packaging_plan
from app.services.recommendations.ranker import rank_recommendations

router = APIRouter(prefix="/runs", tags=["recommendations"])


@router.post("/{run_id}/recommendations/draft", response_model=RecommendationDraftResponse)
def draft_recommendations(run_id: UUID) -> RecommendationDraftResponse:
    run = RUN_STORE.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.synthesized_evidence is None:
        raise HTTPException(
            status_code=400,
            detail="Synthesize evidence first before drafting recommendations.",
        )

    audience_analysis = analyze_audience_psychology(run)
    candidates = generate_candidate_ideas(run, audience_analysis)

    packaging_plans = {
        candidate.id: create_packaging_plan(candidate, run, audience_analysis)
        for candidate in candidates
    }

    final_recommendations = rank_recommendations(
        candidates=candidates,
        packaging_plans=packaging_plans,
        run=run,
        audience=audience_analysis,
    )

    return RecommendationDraftResponse(
        audience_analysis=audience_analysis,
        candidates=candidates,
        final_recommendations=final_recommendations,
    )