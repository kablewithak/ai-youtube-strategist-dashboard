from __future__ import annotations

from pathlib import Path

from app.schemas.strategy import PlaybookChunk


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _read_if_exists(relative_path: str) -> str | None:
    path = _repo_root() / relative_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


EMOTIONAL_PSYCHOLOGY_FALLBACK = """
People act to resolve inner tensions, not just because information is useful.
Strong recurring tensions include status, belonging, relief, safety, identity, shame reduction, control, and self-repair.
Use this file to interpret why an audience cares, not just what they clicked.
Questions:
- What is hurting, missing, threatening, or hungry inside the viewer?
- Who do they want to become, protect, return to, or prove they are?
- Is this audience seeking competence, calm, admiration, belonging, validation, or meaning?
"""

CTA_TIMING_FALLBACK = """
The best CTA comes right after the emotional moment that makes the ask feel natural.
Map CTA timing to the emotional spike:
- curiosity -> keep watching
- trust -> subscribe
- recognition -> comment
- utility -> save or click
- proof -> buy, book, apply
- satisfaction -> watch next
Match by video type:
- educational: after first useful breakthrough or proof moment
- vlog: after warmth, vulnerability, or companionship
- commentary: after a strong insight or recognition beat
- review: after verdict or demonstrated proof
"""

CTA_TEMPLATES_FALLBACK = """
CTA families:
- subscribe
- watch next
- comment
- share
- save
- link/resource
- buy/book/apply
- newsletter/community
Use the CTA family only after the correct emotional groundwork exists.
Low-friction asks come earlier than high-friction asks.
"""

TITLE_STRUCTURES_FALLBACK = """
There is no universal best title. Title structure should match viewer state and traffic source.
Main title families:
- searchable/how-to
- curiosity/open loop
- test/experiment
- transformation
- comparison/ranking
- confession/reveal
- vlog/check-in
- ambition/status
- pain-point/mistake
- psychology/recognition
Choose title families based on the viewer state and content angle, not by copying viral phrasing blindly.
"""

TITLE_THUMBNAIL_FALLBACK = """
Title = tension.
Thumbnail = one clear emotional image.
Video = promise kept.

Thumbnail drivers:
- curiosity
- shame relief
- status
- belonging
- comfort
- proof
- transformation
- threat/risk
- parasocial closeness
- identity transition

Use one dominant emotional signal only. Do not clutter the thumbnail angle.
"""


def load_playbook_registry() -> dict[str, PlaybookChunk]:
    emotional_text = _read_if_exists(
        "packages/prompt-assets/strategist_playbooks/emotional_psychology.md"
    ) or EMOTIONAL_PSYCHOLOGY_FALLBACK

    cta_timing_text = _read_if_exists(
        "packages/prompt-assets/strategist_playbooks/cta_timing.md"
    ) or CTA_TIMING_FALLBACK

    cta_templates_text = _read_if_exists(
        "packages/prompt-assets/strategist_playbooks/cta_templates.md"
    ) or CTA_TEMPLATES_FALLBACK

    title_structures_text = _read_if_exists(
        "packages/prompt-assets/strategist_playbooks/title_structures.md"
    ) or TITLE_STRUCTURES_FALLBACK

    title_thumbnail_text = _read_if_exists(
        "packages/prompt-assets/strategist_playbooks/title_thumbnail_emotional_drivers.md"
    ) or TITLE_THUMBNAIL_FALLBACK

    return {
        "emotional_psychology": PlaybookChunk(
            playbook_id="emotional_psychology",
            title="Emotional Psychology",
            content=emotional_text,
            tags=["audience", "emotion", "identity", "tension", "psychology"],
        ),
        "cta_timing": PlaybookChunk(
            playbook_id="cta_timing",
            title="CTA Timing",
            content=cta_timing_text,
            tags=["cta", "timing", "sequencing", "video_type"],
        ),
        "cta_templates": PlaybookChunk(
            playbook_id="cta_templates",
            title="CTA Templates",
            content=cta_templates_text,
            tags=["cta", "copy", "wording", "conversion"],
        ),
        "title_structures": PlaybookChunk(
            playbook_id="title_structures",
            title="Title Structures",
            content=title_structures_text,
            tags=["titles", "viewer_state", "traffic_source", "packaging"],
        ),
        "title_thumbnail_emotional_drivers": PlaybookChunk(
            playbook_id="title_thumbnail_emotional_drivers",
            title="Title + Thumbnail Emotional Drivers",
            content=title_thumbnail_text,
            tags=["titles", "thumbnails", "emotion", "packaging"],
        ),
    }