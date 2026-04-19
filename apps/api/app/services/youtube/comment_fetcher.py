from __future__ import annotations

from app.schemas.youtube import YouTubeCommentSample, YouTubeVideo
from app.services.youtube.client import YouTubeApiClient, YouTubeApiError


def fetch_comment_samples(
    videos: list[YouTubeVideo],
    per_video_limit: int = 20,
) -> list[YouTubeCommentSample]:
    client = YouTubeApiClient()
    results: list[YouTubeCommentSample] = []

    for video in videos:
        try:
            response = client.comment_threads_list(
                part="snippet",
                videoId=video.video_id,
                maxResults=min(per_video_limit, 100),
                order="relevance",
                textFormat="plainText",
            )
        except YouTubeApiError:
            continue

        items = response.get("items", [])

        for item in items:
            snippet = item.get("snippet", {})
            top_level_comment = snippet.get("topLevelComment", {})
            comment_snippet = top_level_comment.get("snippet", {})

            comment_id = top_level_comment.get("id", "")
            text_display = comment_snippet.get("textDisplay", "") or ""

            if not comment_id or not text_display.strip():
                continue

            results.append(
                YouTubeCommentSample(
                    comment_id=comment_id,
                    video_id=video.video_id,
                    author_display_name=comment_snippet.get("authorDisplayName", "") or "",
                    text_display=text_display.strip(),
                    like_count=comment_snippet.get("likeCount"),
                    published_at=comment_snippet.get("publishedAt", "") or "",
                    updated_at=comment_snippet.get("updatedAt", "") or "",
                )
            )

    return results