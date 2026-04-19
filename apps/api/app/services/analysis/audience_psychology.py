from __future__ import annotations

from app.schemas.run import AnalysisRun
from app.schemas.strategy import AudiencePsychologyOutput, ViewerStateProfile
from app.services.playbooks.selector import select_playbooks


def _collect_confirmed_findings(run: AnalysisRun) -> list[str]:
    findings: list[str] = []

    if run.youtube_channel:
        findings.append(
            f"Resolved YouTube channel: {run.youtube_channel.title}"
        )

        if run.youtube_channel.description:
            findings.append(
                "Channel description is available and can be used as direct creator context."
            )

    if run.evidence_summary:
        findings.append(
            f"Fetched {run.evidence_summary.total_videos_fetched} recent videos."
        )
        findings.append(
            f"Fetched {run.evidence_summary.total_comments_fetched} comment samples."
        )

        if run.evidence_summary.repeated_phrases:
            findings.append(
                "Repeated phrases were detected in audience comments."
            )

        if run.evidence_summary.request_themes:
            findings.append(
                "There are direct viewer request signals in the sampled comments."
            )

        if run.evidence_summary.pain_points:
            findings.append(
                "There are direct pain-point signals in the sampled comments."
            )

    if run.notes.strip():
        findings.append("User-provided notes are available.")

    if run.screenshots:
        findings.append(f"{len(run.screenshots)} screenshot(s) were uploaded.")

    return findings


def _infer_hidden_tensions(run: AnalysisRun) -> list[str]:
    tensions: list[str] = []

    niche = run.channel_niche.lower()
    notes = run.notes.lower()

    if "business" in niche or "money" in niche or "career" in niche:
        tensions.extend(
            [
                "fear of being left behind",
                "desire for competence and control",
                "status anxiety around progress",
            ]
        )

    if "psychology" in niche or "wellness" in niche or "healing" in niche:
        tensions.extend(
            [
                "desire for emotional relief",
                "self-repair and identity clarity",
                "need to feel understood",
            ]
        )

    if "south africa" in notes or "south africa" in str(run.audience_demographics).lower():
        tensions.append("context-specific local relevance matters to the audience")

    if run.evidence_summary and run.evidence_summary.pain_points:
        tensions.append("viewers are looking for clarity around difficult or confusing topics")

    if run.evidence_summary and run.evidence_summary.request_themes:
        tensions.append("viewers want more direct answers and practical follow-ups")

    deduped: list[str] = []
    for item in tensions:
        if item not in deduped:
            deduped.append(item)

    return deduped


def _infer_desired_identity(run: AnalysisRun) -> list[str]:
    desired: list[str] = []
    niche = run.channel_niche.lower()

    if "business" in niche or "money" in niche:
        desired.extend(
            [
                "a more informed and strategic operator",
                "someone who understands leverage and opportunity",
            ]
        )

    if "career" in niche:
        desired.extend(
            [
                "someone who is progressing and not stagnant",
                "someone who looks capable and prepared",
            ]
        )

    if "psychology" in niche or "wellness" in niche:
        desired.extend(
            [
                "someone who understands themselves better",
                "someone more emotionally regulated and self-aware",
            ]
        )

    if not desired:
        desired.extend(
            [
                "someone more informed",
                "someone more confident in their next move",
            ]
        )

    return desired


def _infer_emotional_jobs(run: AnalysisRun) -> list[str]:
    jobs: list[str] = []

    if run.evidence_summary and run.evidence_summary.request_themes:
        jobs.append("give viewers clearer answers")
    if run.evidence_summary and run.evidence_summary.pain_points:
        jobs.append("reduce confusion and uncertainty")
    if run.evidence_summary and run.evidence_summary.praise_themes:
        jobs.append("reward viewers with useful, validating insight")

    niche = run.channel_niche.lower()
    if "business" in niche or "career" in niche:
        jobs.append("help viewers feel more capable and ahead")
    if "psychology" in niche or "wellness" in niche:
        jobs.append("help viewers feel seen, calmer, and more self-aware")

    deduped: list[str] = []
    for item in jobs:
        if item not in deduped:
            deduped.append(item)

    return deduped


def _infer_emotional_drivers(run: AnalysisRun) -> list[str]:
    drivers: list[str] = []

    hidden_tensions = _infer_hidden_tensions(run)

    if any("status" in tension or "behind" in tension for tension in hidden_tensions):
        drivers.append("status")
    if any("control" in tension or "clarity" in tension or "competence" in tension for tension in hidden_tensions):
        drivers.append("control")
    if any("relief" in tension or "confusion" in tension for tension in hidden_tensions):
        drivers.append("relief")
    if any("understood" in tension or "local relevance" in tension for tension in hidden_tensions):
        drivers.append("belonging")
    if any("identity" in tension or "self-repair" in tension for tension in hidden_tensions):
        drivers.append("identity")

    if not drivers:
        drivers.append("curiosity")

    return drivers


def _infer_trust_mode(run: AnalysisRun) -> str:
    if run.evidence_summary and run.evidence_summary.total_comments_fetched > 20:
        return "recognition"

    niche = run.channel_niche.lower()
    if "business" in niche or "money" in niche:
        return "authority"
    if "psychology" in niche or "wellness" in niche:
        return "warmth"

    return "recognition"


def analyze_audience_psychology(run: AnalysisRun) -> AudiencePsychologyOutput:
    playbooks = select_playbooks("audience_psychology")

    evidence_notes = [
        "Audience psychology analysis is grounded in the current run evidence and strategist playbook.",
    ]

    if playbooks:
        evidence_notes.append(
            f"Loaded playbook: {playbooks[0].title}"
        )

    confirmed_findings = _collect_confirmed_findings(run)
    hidden_tensions = _infer_hidden_tensions(run)
    desired_identity = _infer_desired_identity(run)
    emotional_jobs = _infer_emotional_jobs(run)
    emotional_drivers = _infer_emotional_drivers(run)
    trust_mode = _infer_trust_mode(run)

    inferences: list[str] = []
    weak_signals: list[str] = []

    if "context-specific local relevance matters to the audience" in hidden_tensions:
        inferences.append(
            "South African context likely matters to how examples, titles, and recommendations should be framed."
        )

    if run.youtube_channel and run.youtube_channel.description:
        inferences.append(
            "The creator's own channel description should be weighted above isolated flashy titles."
        )
    else:
        weak_signals.append(
            "Channel description evidence is missing or weak."
        )

    if run.evidence_summary and run.evidence_summary.total_comments_fetched < 15:
        weak_signals.append(
            "Comment sample size is still small, so emotional interpretation may be incomplete."
        )

    assumptions_used = [
        f"User-reviewed audience intent: {run.assumptions.audience_intent}",
        f"User-reviewed likely topic patterns: {', '.join(run.assumptions.likely_topic_patterns[:3]) or 'None'}",
    ]

    profile = ViewerStateProfile(
        emotional_jobs=emotional_jobs,
        hidden_tensions=hidden_tensions,
        desired_identity=desired_identity,
        emotional_drivers=emotional_drivers,
        trust_mode=trust_mode,
        evidence_notes=evidence_notes,
    )

    return AudiencePsychologyOutput(
        viewer_state_profile=profile,
        confirmed_findings=confirmed_findings,
        inferences=inferences,
        weak_signals=weak_signals,
        assumptions_used=assumptions_used,
    )