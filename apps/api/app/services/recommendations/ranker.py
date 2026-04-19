from __future__ import annotations

from app.schemas.recommendations import FinalRecommendation, IdeaCandidate, PackagingPlan
from app.schemas.run import AnalysisRun
from app.schemas.strategy import AudiencePsychologyOutput


def _packaging_strength(packaging: PackagingPlan, candidate: IdeaCandidate) -> float:
    score = 0.62

    if packaging.title_options:
        score += 0.08

    if packaging.cta_copy_options:
        score += 0.05

    if candidate.emotional_driver in packaging.thumbnail_driver.lower() or candidate.emotional_driver in packaging.packaging_rationale.lower():
        score += 0.08

    if "south africa" in " ".join(packaging.title_options).lower():
        score += 0.05

    return min(score, 0.9)


def _evidence_strength(candidate: IdeaCandidate, audience: AudiencePsychologyOutput) -> float:
    score = 0.55

    if len(candidate.evidence_anchors) >= 2:
        score += 0.08

    if audience.confirmed_findings:
        score += 0.08

    if audience.weak_signals:
        score -= 0.05

    return max(min(score, 0.9), 0.35)


def _overall_score(
    candidate: IdeaCandidate,
    packaging: PackagingPlan,
    audience: AudiencePsychologyOutput,
) -> float:
    packaging_strength = _packaging_strength(packaging, candidate)
    evidence_strength = _evidence_strength(candidate, audience)

    return (
        candidate.channel_fit_score * 0.30
        + candidate.audience_fit_score * 0.28
        + candidate.trend_score * 0.12
        + packaging_strength * 0.18
        + evidence_strength * 0.12
    )


def rank_recommendations(
    candidates: list[IdeaCandidate],
    packaging_plans: dict[str, PackagingPlan],
    run: AnalysisRun,
    audience: AudiencePsychologyOutput,
) -> list[FinalRecommendation]:
    scored_rows = []

    for candidate in candidates:
        packaging = packaging_plans[candidate.id]
        score = _overall_score(candidate, packaging, audience)
        scored_rows.append((score, candidate, packaging))

    scored_rows.sort(key=lambda row: row[0], reverse=True)

    final_recommendations: list[FinalRecommendation] = []

    for rank, (_, candidate, packaging) in enumerate(scored_rows[:10], start=1):
        why_this_fits_parts = [
            f"It addresses the viewer tension around {candidate.target_viewer_state}.",
            f"It leans into the emotional driver '{candidate.emotional_driver}'.",
            f"It is grounded in evidence anchors: {', '.join(candidate.evidence_anchors[:3])}.",
        ]

        if "south africa" in candidate.topic.lower():
            why_this_fits_parts.append("It is better localized to the South African context already present in the run.")

        final_recommendations.append(
            FinalRecommendation(
                rank=rank,
                idea=f"{candidate.topic} — {candidate.angle}",
                hook=f"Start with the tension around {candidate.target_viewer_state}, then show why {candidate.topic.lower()} matters now.",
                title_options=packaging.title_options,
                thumbnail_angle=packaging.thumbnail_angle,
                structure=packaging.video_structure,
                cta_placement=packaging.cta_timing,
                cta_copy=packaging.cta_copy_options,
                why_this_fits=" ".join(why_this_fits_parts),
                evidence_notes=[
                    *candidate.evidence_anchors[:3],
                    *candidate.trend_anchors[:2],
                ],
            )
        )

    return final_recommendations