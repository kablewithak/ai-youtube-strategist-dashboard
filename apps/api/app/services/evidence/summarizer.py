from __future__ import annotations

import re
from collections import Counter

from app.schemas.run import AssumptionSet
from app.schemas.youtube import EvidenceSummary, YouTubeCommentSample, YouTubeVideo

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "you",
    "your",
    "are",
    "was",
    "have",
    "has",
    "but",
    "from",
    "they",
    "them",
    "would",
    "could",
    "about",
    "into",
    "what",
    "when",
    "where",
    "which",
    "their",
    "there",
    "just",
    "really",
    "very",
    "more",
    "like",
    "been",
    "being",
    "than",
    "then",
    "also",
    "make",
    "made",
    "video",
    "videos",
    "how",
    "why",
    "what",
    "here",
    "there",
    "world",
    "client",
}


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_repeated_phrases(
    comments: list[YouTubeCommentSample],
    limit: int = 8,
) -> list[str]:
    bigram_counter: Counter[str] = Counter()

    for comment in comments:
        normalized = _normalize_text(comment.text_display)
        words = [
            word
            for word in normalized.split()
            if word and word not in STOPWORDS and len(word) > 2
        ]

        for index in range(len(words) - 1):
            phrase = f"{words[index]} {words[index + 1]}"
            bigram_counter[phrase] += 1

    repeated = [
        phrase
        for phrase, count in bigram_counter.most_common()
        if count >= 2
    ]

    return repeated[:limit]


def _extract_topic_patterns_from_videos(
    videos: list[YouTubeVideo],
    limit: int = 5,
) -> list[str]:
    phrase_counter: Counter[str] = Counter()

    for video in videos:
        combined = f"{video.title} {video.description}"
        normalized = _normalize_text(combined)
        words = [
            word
            for word in normalized.split()
            if word and word not in STOPWORDS and len(word) > 3
        ]

        for index in range(len(words) - 1):
            phrase = f"{words[index]} {words[index + 1]}"
            phrase_counter[phrase] += 1

    candidates = [
        phrase
        for phrase, count in phrase_counter.most_common()
        if count >= 2
    ]

    cleaned: list[str] = []
    for phrase in candidates:
        if phrase not in cleaned:
            cleaned.append(phrase)

    return cleaned[:limit]


def summarize_evidence(
    videos: list[YouTubeVideo],
    comments: list[YouTubeCommentSample],
) -> EvidenceSummary:
    normalized_comments = [_normalize_text(comment.text_display) for comment in comments]

    praise_count = sum(
        1
        for text in normalized_comments
        if _contains_any(
            text,
            ["love", "great", "amazing", "helpful", "useful", "best", "excellent"],
        )
    )

    request_count = sum(
        1
        for text in normalized_comments
        if _contains_any(
            text,
            ["please", "can you", "could you", "would love", "want", "need", "make a video"],
        )
    )

    pain_count = sum(
        1
        for text in normalized_comments
        if _contains_any(
            text,
            ["confused", "struggle", "hard", "difficult", "problem", "issue", "dont understand", "do not understand"],
        )
    )

    praise_themes: list[str] = []
    request_themes: list[str] = []
    pain_points: list[str] = []

    if praise_count > 0:
        praise_themes.append(
            "Viewers respond positively to content they find useful, insightful, or valuable."
        )
    if request_count > 0:
        request_themes.append(
            "Commenters are asking for follow-ups, deeper breakdowns, or direct answers."
        )
    if pain_count > 0:
        pain_points.append(
            "Some commenters are expressing confusion, difficulty, or unresolved problems."
        )

    repeated_phrases = _extract_repeated_phrases(comments)

    evidence_notes = [
        f"Fetched {len(videos)} recent videos.",
        f"Fetched {len(comments)} top-level comment samples.",
    ]

    if repeated_phrases:
        evidence_notes.append("Repeated phrases were detected across the sampled comments.")
    if not comments:
        evidence_notes.append("No comments were available in the current sample.")
    if not videos:
        evidence_notes.append("No recent videos were returned for the resolved channel.")

    return EvidenceSummary(
        total_videos_fetched=len(videos),
        total_comments_fetched=len(comments),
        top_video_titles=[video.title for video in videos[:5]],
        repeated_phrases=repeated_phrases,
        praise_themes=praise_themes,
        request_themes=request_themes,
        pain_points=pain_points,
        evidence_notes=evidence_notes,
    )


def build_assumptions_from_evidence(
    channel_niche: str,
    summary: EvidenceSummary,
    videos: list[YouTubeVideo],
) -> AssumptionSet:
    audience_interests = summary.repeated_phrases[:4]

    if not audience_interests:
        audience_interests = [
            f"{channel_niche} advice",
            f"{channel_niche} practical insights",
            f"{channel_niche} explainers",
        ]

    derived_topic_patterns = _extract_topic_patterns_from_videos(videos)

    likely_topic_patterns = derived_topic_patterns[:4]
    if not likely_topic_patterns:
        likely_topic_patterns = [
            f"{channel_niche} explainers",
            f"{channel_niche} commentary",
            f"{channel_niche} practical breakdowns",
        ]

    intent_parts: list[str] = []

    if summary.request_themes:
        intent_parts.append(
            "The audience appears to want more direct answers and follow-up content."
        )
    if summary.pain_points:
        intent_parts.append(
            "There are signs that viewers want clarity on difficult or confusing topics."
        )
    if not intent_parts:
        intent_parts.append(
            "The audience likely wants useful, relevant content that is easy to apply and understand."
        )

    confidence_parts = [
        "These assumptions were drafted from fetched YouTube titles, descriptions, and sampled top-level comments.",
        "They are more grounded than placeholders, but still limited by the current sample size.",
    ]

    return AssumptionSet(
        audience_interests=audience_interests,
        likely_topic_patterns=likely_topic_patterns,
        audience_intent=" ".join(intent_parts),
        screenshot_interpretation="No screenshot analysis has been run yet.",
        confidence_notes=" ".join(confidence_parts),
    )