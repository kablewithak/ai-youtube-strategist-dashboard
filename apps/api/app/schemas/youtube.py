from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ChannelIdentifierType = Literal["handle", "channel_id", "custom_name", "username"]


class ParsedYouTubeChannelUrl(BaseModel):
    source_url: str
    identifier_type: ChannelIdentifierType
    identifier: str


class YouTubeChannel(BaseModel):
    channel_id: str
    title: str
    description: str = ""
    custom_url: str = ""
    published_at: str = ""
    uploads_playlist_id: str = ""
    subscriber_count: int | None = None
    video_count: int | None = None
    view_count: int | None = None
    thumbnails: dict[str, str] = Field(default_factory=dict)


class YouTubeVideo(BaseModel):
    video_id: str
    channel_id: str
    channel_title: str
    title: str
    description: str = ""
    published_at: str = ""
    url: str = ""
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None


class YouTubeCommentSample(BaseModel):
    comment_id: str
    video_id: str
    author_display_name: str
    text_display: str
    like_count: int | None = None
    published_at: str = ""
    updated_at: str = ""


class EvidenceSummary(BaseModel):
    total_videos_fetched: int = 0
    total_comments_fetched: int = 0
    top_video_titles: list[str] = Field(default_factory=list)
    repeated_phrases: list[str] = Field(default_factory=list)
    praise_themes: list[str] = Field(default_factory=list)
    request_themes: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)