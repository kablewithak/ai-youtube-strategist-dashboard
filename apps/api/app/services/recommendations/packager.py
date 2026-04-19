from __future__ import annotations

from app.schemas.recommendations import IdeaCandidate, PackagingPlan
from app.schemas.run import AnalysisRun
from app.schemas.strategy import AudiencePsychologyOutput
from app.services.playbooks.selector import select_playbooks


def _has_south_african_context(run: AnalysisRun, audience: AudiencePsychologyOutput) -> bool:
    demographic_text = str(run.audience_demographics).lower()
    notes_text = run.notes.lower()

    if "south africa" in demographic_text or "south africa" in notes_text:
        return True

    return any("south africa" in item.lower() for item in audience.inferences)


def _infer_title_family(candidate: IdeaCandidate) -> str:
    driver = candidate.emotional_driver

    if driver == "control":
        return "searchable/how-to"
    if driver == "relief":
        return "pain-point/mistake"
    if driver == "identity":
        return "transformation/identity"
    if driver == "status":
        return "ambition/status"
    if driver == "belonging":
        return "psychology/recognition"
    return "curiosity/open-loop"


def _generate_title_options(
    candidate: IdeaCandidate,
    run: AnalysisRun,
    audience: AudiencePsychologyOutput,
    title_family: str,
) -> list[str]:
    topic = candidate.topic.strip()
    topic_lower = topic.lower()
    has_sa_context = _has_south_african_context(run, audience)

    if title_family == "searchable/how-to":
        options = [
            f"How to think about {topic_lower} with more clarity",
            f"A practical guide to {topic_lower}",
            f"What actually matters when it comes to {topic_lower}",
        ]
    elif title_family == "pain-point/mistake":
        options = [
            f"The mistake people make with {topic_lower}",
            f"Why {topic_lower} still feels confusing",
            f"What most people miss about {topic_lower}",
        ]
    elif title_family == "transformation/identity":
        options = [
            f"What changes when you understand {topic_lower}",
            f"The identity shift behind {topic_lower}",
            f"How {topic_lower} changes the way you move",
        ]
    elif title_family == "ambition/status":
        options = [
            f"How to approach {topic_lower} without getting left behind",
            f"What strong performers understand about {topic_lower}",
            f"The smarter way to think about {topic_lower}",
        ]
    elif title_family == "psychology/recognition":
        options = [
            f"The psychology behind {topic_lower}",
            f"Why people keep getting stuck on {topic_lower}",
            f"What {topic_lower} really says about where people are at",
        ]
    else:
        options = [
            f"What people are getting wrong about {topic_lower}",
            f"The part everyone misses about {topic_lower}",
            f"Why {topic_lower} matters more than people think",
        ]

    if has_sa_context and not any("south africa" in option.lower() for option in options):
        options[1] = f"{options[1]} in South Africa"

    return options


def _choose_thumbnail_driver(candidate: IdeaCandidate) -> str:
    driver = candidate.emotional_driver

    if driver == "status":
        return "status"
    if driver == "control":
        return "clarity/control"
    if driver == "relief":
        return "relief"
    if driver == "identity":
        return "identity shift"
    if driver == "belonging":
        return "recognition/belonging"
    return "curiosity"


def _choose_thumbnail_angle(
    candidate: IdeaCandidate,
    run: AnalysisRun,
    audience: AudiencePsychologyOutput,
) -> str:
    has_sa_context = _has_south_african_context(run, audience)

    if candidate.emotional_driver == "status":
        base = "Direct eye contact, one tension phrase, and a visual cue of progress or advantage."
    elif candidate.emotional_driver == "control":
        base = "Concerned expression, one key term, and a clean visual showing signal vs noise."
    elif candidate.emotional_driver == "relief":
        base = "Confused-to-clear contrast with one calm, low-clutter visual anchor."
    elif candidate.emotional_driver == "identity":
        base = "Before-versus-after identity cue with one phrase that signals growth or change."
    elif candidate.emotional_driver == "belonging":
        base = "Recognition-driven facial expression with a phrase that makes the viewer feel seen."
    else:
        base = "One unresolved clue, one emotional face, and minimal text."

    if has_sa_context and "south africa" in candidate.topic.lower():
        base += " Include a subtle South African context cue rather than a generic global frame."

    return base


def _choose_video_structure(candidate: IdeaCandidate) -> list[str]:
    return [
        f"Open with the viewer tension: {candidate.target_viewer_state}.",
        f"Explain why {candidate.topic.lower()} matters right now.",
        "Break the topic into a simple framework or practical lens.",
        "Use one concrete example, case, or local-context reference.",
        "Close with a clear takeaway and a natural CTA.",
    ]


def _choose_cta_type(candidate: IdeaCandidate) -> str:
    if candidate.emotional_driver == "relief":
        return "save"
    if candidate.emotional_driver == "belonging":
        return "comment"
    if candidate.emotional_driver == "status":
        return "watch_next"
    if candidate.emotional_driver == "control":
        return "subscribe"
    if candidate.emotional_driver == "identity":
        return "comment"
    return "subscribe"


def _choose_cta_timing(candidate: IdeaCandidate, cta_type: str) -> str:
    if cta_type == "save":
        return "Place the CTA right after the practical framework or checklist moment."
    if cta_type == "comment":
        return "Place the CTA right after the strongest recognition or resonance line."
    if cta_type == "watch_next":
        return "Place the CTA after the payoff or clarity moment, when momentum is highest."
    return "Place the CTA right after the first strong useful insight or proof beat."


def _choose_cta_copy(cta_type: str, run: AnalysisRun) -> list[str]:
    niche = run.channel_niche.lower()

    if cta_type == "save":
        return [
            "Save this so you can come back to it when you need it.",
            f"Bookmark this if you're trying to get better at {niche}.",
        ]

    if cta_type == "comment":
        return [
            "Comment if this is something you've noticed too.",
            "Tell me which part of this hit the hardest for you.",
        ]

    if cta_type == "watch_next":
        return [
            "Watch the next video if you want the deeper version of this.",
            "Keep the momentum going and watch the next breakdown.",
        ]

    return [
        "If you want more practical breakdowns like this, subscribe.",
        f"Subscribe if you want more no-fluff videos on {niche}.",
    ]


def create_packaging_plan(
    candidate: IdeaCandidate,
    run: AnalysisRun,
    audience: AudiencePsychologyOutput,
) -> PackagingPlan:
    playbooks = select_playbooks("full_packaging")
    title_family = _infer_title_family(candidate)
    title_options = _generate_title_options(candidate, run, audience, title_family)
    thumbnail_driver = _choose_thumbnail_driver(candidate)
    thumbnail_angle = _choose_thumbnail_angle(candidate, run, audience)
    video_structure = _choose_video_structure(candidate)
    cta_type = _choose_cta_type(candidate)
    cta_timing = _choose_cta_timing(candidate, cta_type)
    cta_copy_options = _choose_cta_copy(cta_type, run)

    playbook_names = ", ".join(playbook.title for playbook in playbooks) if playbooks else "No playbooks loaded"

    packaging_rationale = (
        f"Packaging is built around the viewer state '{candidate.target_viewer_state}' "
        f"and the emotional driver '{candidate.emotional_driver}'. "
        f"Selected title family: {title_family}. "
        f"Playbooks used: {playbook_names}."
    )

    return PackagingPlan(
        title_family=title_family,
        title_options=title_options,
        thumbnail_driver=thumbnail_driver,
        thumbnail_angle=thumbnail_angle,
        video_structure=video_structure,
        cta_type=cta_type,
        cta_timing=cta_timing,
        cta_copy_options=cta_copy_options,
        packaging_rationale=packaging_rationale,
    )