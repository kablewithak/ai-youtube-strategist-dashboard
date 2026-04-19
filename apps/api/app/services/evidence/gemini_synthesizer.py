from __future__ import annotations

from typing import Any

from google import genai
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.evidence import SynthesizedEvidence
from app.schemas.run import AnalysisRun


class GeminiSynthesisResult(BaseModel):
    channel_summary: str = ""
    audience_mood: str = ""
    praise_themes: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    request_themes: list[str] = Field(default_factory=list)
    repeated_phrases: list[str] = Field(default_factory=list)
    evidence_strength_notes: list[str] = Field(default_factory=list)


def _build_compiled_text(run: AnalysisRun) -> str:
    parts: list[str] = []

    parts.append("=== RUN CONTEXT ===")
    parts.append(f"Channel URL: {run.channel_url}")
    parts.append(f"Channel niche: {run.channel_niche}")
    parts.append(f"Channel goals: {run.channel_goals}")
    parts.append(f"Audience demographics: {run.audience_demographics}")
    parts.append(f"Notes: {run.notes or 'None provided'}")
    parts.append("")

    if run.youtube_channel:
        channel = run.youtube_channel
        parts.append("=== YOUTUBE CHANNEL ===")
        parts.append(f"Title: {channel.title}")
        parts.append(f"Custom URL: {channel.custom_url}")
        parts.append(f"Description: {channel.description}")
        parts.append(f"Subscriber count: {channel.subscriber_count}")
        parts.append(f"Video count: {channel.video_count}")
        parts.append(f"View count: {channel.view_count}")
        parts.append("")

    if run.videos:
        parts.append("=== RECENT VIDEOS ===")
        for index, video in enumerate(run.videos[:10], start=1):
            parts.append(
                f"{index}. Title: {video.title}\n"
                f"   Description: {video.description}\n"
                f"   Views: {video.view_count}, Likes: {video.like_count}, Comments: {video.comment_count}"
            )
        parts.append("")

    if run.comment_samples:
        parts.append("=== COMMENT SAMPLES ===")
        for index, comment in enumerate(run.comment_samples[:40], start=1):
            parts.append(f"{index}. {comment.author_display_name}: {comment.text_display}")
        parts.append("")

    if run.evidence_summary:
        summary = run.evidence_summary
        parts.append("=== DETERMINISTIC EVIDENCE SUMMARY ===")
        parts.append(f"Top video titles: {summary.top_video_titles}")
        parts.append(f"Repeated phrases: {summary.repeated_phrases}")
        parts.append(f"Praise themes: {summary.praise_themes}")
        parts.append(f"Request themes: {summary.request_themes}")
        parts.append(f"Pain points: {summary.pain_points}")
        parts.append(f"Evidence notes: {summary.evidence_notes}")
        parts.append("")

    parts.append("=== USER-REVIEWED ASSUMPTIONS ===")
    parts.append(run.assumptions.model_dump_json(indent=2))

    return "\n".join(parts)


def synthesize_run_evidence(run: AnalysisRun) -> SynthesizedEvidence:
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to apps/api/.env and restart the backend."
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    compiled_text = _build_compiled_text(run)

    prompt = f"""
You are an evidence-first YouTube strategist analyst.

Your job:
1. Read the compiled channel evidence and any uploaded screenshots.
2. Produce grounded synthesis only.
3. Treat the audience demographics, geography, channel niche, channel description, and user notes as high-priority context.
4. Do not casually import flashy or generic themes from isolated titles.
5. If a title appears clickbait, off-market, or weakly supported, say the evidence is weak instead of treating it as a core audience theme.
6. Preserve the user's reviewed assumptions as user-owned inputs. Do not replace them.
7. Use South African context if the demographics or notes indicate South Africa.
8. Keep outputs concise, specific, and useful for a strategist dashboard.

Return JSON matching the schema exactly.

Rules:
- channel_summary should describe what the channel appears to focus on based on repeated evidence, not one-off flashy titles.
- audience_mood should reflect comments and evidence tone.
- praise_themes, pain_points, request_themes, repeated_phrases should be concise and evidence-backed.
- evidence_strength_notes should clearly mention when evidence is weak, conflicting, or imported from too few examples.
- If the fetched evidence appears mismatched to the declared channel context, state that directly.

Compiled evidence:
{compiled_text}
""".strip()

    contents: list[Any] = []

    for screenshot in run.screenshots:
        uploaded_file = client.files.upload(file=screenshot.local_path)
        contents.append(uploaded_file)

    contents.append(prompt)

    response = client.models.generate_content(
        model=settings.gemini_synthesis_model,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": GeminiSynthesisResult.model_json_schema(),
        },
    )

    result = GeminiSynthesisResult.model_validate_json(response.text)

    return SynthesizedEvidence(
        channel_summary=result.channel_summary,
        audience_mood=result.audience_mood,
        praise_themes=result.praise_themes,
        pain_points=result.pain_points,
        request_themes=result.request_themes,
        repeated_phrases=result.repeated_phrases,
        evidence_strength_notes=result.evidence_strength_notes,
    )