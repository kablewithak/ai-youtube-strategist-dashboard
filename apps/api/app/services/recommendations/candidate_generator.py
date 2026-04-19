from __future__ import annotations

from uuid import uuid4

from app.schemas.recommendations import IdeaCandidate
from app.schemas.run import AnalysisRun
from app.schemas.strategy import AudiencePsychologyOutput


def _has_south_african_context(run: AnalysisRun, audience: AudiencePsychologyOutput) -> bool:
    demographic_text = str(run.audience_demographics).lower()
    notes_text = run.notes.lower()

    if "south africa" in demographic_text or "south africa" in notes_text:
        return True

    return any("south african" in item.lower() or "south africa" in item.lower() for item in audience.inferences)


def _clean_phrase(value: str) -> str:
    text = (value or "").strip().strip(".")
    text = text.replace("Viewers respond positively to ", "")
    text = text.replace("Commenters are asking for ", "")
    text = text.replace("Some commenters are expressing ", "")
    text = text.replace("The audience appears to want ", "")
    text = text.replace("There are signs that viewers want ", "")
    return text.strip().capitalize()


def _extract_theme_pool(run: AnalysisRun) -> list[str]:
    themes: list[str] = []

    themes.extend(run.assumptions.audience_interests[:5])
    themes.extend(run.assumptions.likely_topic_patterns[:5])

    if run.evidence_summary:
        themes.extend(run.evidence_summary.repeated_phrases[:5])
        themes.extend(run.evidence_summary.request_themes[:3])
        themes.extend(run.evidence_summary.pain_points[:3])
        themes.extend(run.evidence_summary.praise_themes[:3])

    if run.synthesized_evidence:
        themes.extend(run.synthesized_evidence.request_themes[:4])
        themes.extend(run.synthesized_evidence.pain_points[:4])
        themes.extend(run.synthesized_evidence.repeated_phrases[:4])
        themes.extend(run.synthesized_evidence.praise_themes[:4])

    deduped: list[str] = []
    for theme in themes:
        cleaned = _clean_phrase(theme)
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)

    if not deduped:
        deduped.append(run.channel_niche.title())

    return deduped


def _pick_emotional_driver(index: int, audience: AudiencePsychologyOutput) -> str:
    drivers = audience.viewer_state_profile.emotional_drivers or ["curiosity"]
    return drivers[index % len(drivers)]


def _pick_target_viewer_state(index: int, audience: AudiencePsychologyOutput) -> str:
    tensions = audience.viewer_state_profile.hidden_tensions or ["need for more clarity"]
    return tensions[index % len(tensions)]


def _score_candidate_base(theme: str, emotional_driver: str, run: AnalysisRun, is_local: bool) -> tuple[float, float, float]:
    channel_fit = 0.72
    audience_fit = 0.72
    trend_score = 0.52

    theme_lower = theme.lower()
    niche_lower = run.channel_niche.lower()

    if any(word in theme_lower for word in niche_lower.split()):
        channel_fit += 0.08

    if emotional_driver in {"status", "control", "relief", "identity", "belonging"}:
        audience_fit += 0.06

    if run.evidence_summary and run.evidence_summary.request_themes:
        trend_score += 0.05

    if is_local:
        channel_fit += 0.06
        audience_fit += 0.06

    return (
        min(channel_fit, 0.95),
        min(audience_fit, 0.95),
        min(trend_score, 0.85),
    )


def generate_candidate_ideas(
    run: AnalysisRun,
    audience: AudiencePsychologyOutput,
) -> list[IdeaCandidate]:
    theme_pool = _extract_theme_pool(run)
    has_sa_context = _has_south_african_context(run, audience)

    base_angles = [
        "a practical explainer people can use immediately",
        "a mistake-based breakdown that reduces confusion",
        "a direct answer to the question viewers keep circling around",
        "a framework that helps viewers think more clearly",
        "a myth-busting angle that corrects weak assumptions",
        "a case-study style breakdown with real-world relevance",
        "a local-context angle that makes the topic more usable",
        "a psychology angle that explains why the issue matters",
        "a next-step guide that gives viewers a clearer move",
        "a comparison angle that separates signal from noise",
        "a contrarian truth that challenges lazy assumptions",
        "a viewer-request-led follow-up with better clarity",
    ]

    candidates: list[IdeaCandidate] = []

    for index, angle in enumerate(base_angles):
        theme = theme_pool[index % len(theme_pool)]
        emotional_driver = _pick_emotional_driver(index, audience)
        target_viewer_state = _pick_target_viewer_state(index, audience)

        topic = theme
        if has_sa_context and index in {2, 6, 9}:
            topic = f"{theme} in South Africa"

        evidence_anchors = [theme]
        if run.youtube_channel:
            evidence_anchors.append(f"Channel: {run.youtube_channel.title}")
        if run.synthesized_evidence and run.synthesized_evidence.channel_summary:
            evidence_anchors.append("Synthesized channel summary available")

        trend_anchors = []
        if run.evidence_summary and run.evidence_summary.request_themes:
            trend_anchors.append("Direct viewer requests detected")
        if run.evidence_summary and run.evidence_summary.repeated_phrases:
            trend_anchors.append("Repeated audience phrases detected")

        channel_fit_score, audience_fit_score, trend_score = _score_candidate_base(
            theme=theme,
            emotional_driver=emotional_driver,
            run=run,
            is_local=has_sa_context and "south africa" in topic.lower(),
        )

        candidates.append(
            IdeaCandidate(
                id=uuid4().hex[:12],
                topic=topic,
                angle=angle,
                target_viewer_state=target_viewer_state,
                emotional_driver=emotional_driver,
                evidence_anchors=evidence_anchors,
                trend_anchors=trend_anchors,
                channel_fit_score=channel_fit_score,
                audience_fit_score=audience_fit_score,
                trend_score=trend_score,
            )
        )

    return candidates