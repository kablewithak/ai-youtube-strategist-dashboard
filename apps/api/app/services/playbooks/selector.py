from __future__ import annotations

from app.schemas.strategy import PlaybookChunk
from app.services.playbooks.registry import load_playbook_registry


def select_playbooks(task_type: str) -> list[PlaybookChunk]:
    registry = load_playbook_registry()

    mapping = {
        "audience_psychology": ["emotional_psychology"],
        "title_packaging": [
            "title_structures",
            "title_thumbnail_emotional_drivers",
        ],
        "cta_planning": [
            "cta_timing",
            "cta_templates",
        ],
        "full_packaging": [
            "title_structures",
            "title_thumbnail_emotional_drivers",
            "cta_timing",
            "cta_templates",
        ],
    }

    selected_ids = mapping.get(task_type, [])
    return [registry[playbook_id] for playbook_id in selected_ids if playbook_id in registry]