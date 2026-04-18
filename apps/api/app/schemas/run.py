from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.youtube import EvidenceSummary, YouTubeChannel, YouTubeCommentSample, YouTubeVideo


class RunStatus:
    DRAFT = "draft"
    INTAKE_SUBMITTED = "intake_submitted"
    ASSUMPTIONS_DRAFTED = "assumptions_drafted"
    ASSUMPTIONS_REVIEWED = "assumptions_reviewed"
    YOUTUBE_INGESTED = "youtube_ingested"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AssumptionSet(BaseModel):
    audience_interests: list[str] = Field(default_factory=list)
    likely_topic_patterns: list[str] = Field(default_factory=list)
    audience_intent: str = ""
    screenshot_interpretation: str = ""
    confidence_notes: str = ""


class CreateRunRequest(BaseModel):
    channel_url: str
    channel_niche: str
    channel_goals: str
    audience_demographics: dict[str, Any] = Field(default_factory=dict)
    notes: str = ""


class UpdateAssumptionsRequest(BaseModel):
    assumptions: AssumptionSet


class AnalysisRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: str = RunStatus.DRAFT

    channel_url: str
    channel_niche: str
    channel_goals: str
    audience_demographics: dict[str, Any] = Field(default_factory=dict)
    notes: str = ""

    assumptions: AssumptionSet = Field(default_factory=AssumptionSet)

    youtube_channel: YouTubeChannel | None = None
    videos: list[YouTubeVideo] = Field(default_factory=list)
    comment_samples: list[YouTubeCommentSample] = Field(default_factory=list)
    evidence_summary: EvidenceSummary | None = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)