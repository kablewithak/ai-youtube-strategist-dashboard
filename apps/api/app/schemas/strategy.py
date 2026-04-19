from __future__ import annotations

from pydantic import BaseModel, Field


class ViewerStateProfile(BaseModel):
    emotional_jobs: list[str] = Field(default_factory=list)
    hidden_tensions: list[str] = Field(default_factory=list)
    desired_identity: list[str] = Field(default_factory=list)
    emotional_drivers: list[str] = Field(default_factory=list)
    trust_mode: str = "recognition"
    evidence_notes: list[str] = Field(default_factory=list)


class PlaybookChunk(BaseModel):
    playbook_id: str
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)


class AudiencePsychologyOutput(BaseModel):
    viewer_state_profile: ViewerStateProfile
    confirmed_findings: list[str] = Field(default_factory=list)
    inferences: list[str] = Field(default_factory=list)
    weak_signals: list[str] = Field(default_factory=list)
    assumptions_used: list[str] = Field(default_factory=list)