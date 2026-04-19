from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


EvidenceKind = Literal["screenshot", "note_file", "compiled_text"]


class ScreenshotEvidence(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: EvidenceKind = "screenshot"
    original_filename: str
    stored_filename: str
    local_path: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=utc_now)


class SynthesizedEvidence(BaseModel):
    channel_summary: str = ""
    audience_mood: str = ""
    praise_themes: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    request_themes: list[str] = Field(default_factory=list)
    repeated_phrases: list[str] = Field(default_factory=list)
    evidence_strength_notes: list[str] = Field(default_factory=list)