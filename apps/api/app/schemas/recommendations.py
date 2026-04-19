from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.strategy import AudiencePsychologyOutput


class TrendSignal(BaseModel):
    topic: str
    source: str
    freshness: str
    confidence: float
    channel_fit: float
    audience_fit: float
    why_now: str


class IdeaCandidate(BaseModel):
    id: str
    topic: str
    angle: str
    target_viewer_state: str
    emotional_driver: str
    evidence_anchors: list[str] = Field(default_factory=list)
    trend_anchors: list[str] = Field(default_factory=list)
    channel_fit_score: float = 0.0
    audience_fit_score: float = 0.0
    trend_score: float = 0.0


class PackagingPlan(BaseModel):
    title_family: str
    title_options: list[str] = Field(default_factory=list)
    thumbnail_driver: str
    thumbnail_angle: str
    video_structure: list[str] = Field(default_factory=list)
    cta_type: str
    cta_timing: str
    cta_copy_options: list[str] = Field(default_factory=list)
    packaging_rationale: str


class FinalRecommendation(BaseModel):
    rank: int
    idea: str
    hook: str
    title_options: list[str] = Field(default_factory=list)
    thumbnail_angle: str
    structure: list[str] = Field(default_factory=list)
    cta_placement: str
    cta_copy: list[str] = Field(default_factory=list)
    why_this_fits: str
    evidence_notes: list[str] = Field(default_factory=list)


class RecommendationDraftResponse(BaseModel):
    audience_analysis: AudiencePsychologyOutput
    candidates: list[IdeaCandidate] = Field(default_factory=list)
    final_recommendations: list[FinalRecommendation] = Field(default_factory=list)