from __future__ import annotations

from app.schemas.youtube import YouTubeChannel, YouTubeVideo
from app.services.youtube.client import YouTubeApiClient


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def fetch_recent_videos(channel: YouTubeChannel, limit: int = 10) -> list[YouTubeVideo]:
    if not channel.uploads_playlist_id:
        return []

    client = YouTubeApiClient()

    playlist_response = client.playlist_items_list(
        part="snippet,contentDetails",
        playlistId=channel.uploads_playlist_id,
        maxResults=min(limit, 50),
    )

    playlist_items = playlist_response.get("items", [])
    if not playlist_items:
        return []

    ordered_video_ids: list[str] = []

    for item in playlist_items:
        content_details = item.get("contentDetails", {})
        snippet = item.get("snippet", {})
        resource = snippet.get("resourceId", {})

        video_id = (
            content_details.get("videoId")
            or resource.get("videoId")
            or ""
        ).strip()

        if video_id:
            ordered_video_ids.append(video_id)

    if not ordered_video_ids:
        return []

    videos_response = client.videos_list(
        part="snippet,statistics",
        id=",".join(ordered_video_ids),
        maxResults=len(ordered_video_ids),
    )

    mapped: dict[str, YouTubeVideo] = {}

    for item in videos_response.get("items", []):
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        video_id = item.get("id", "")

        if snippet.get("channelId", "") != channel.channel_id:
            continue

        mapped[video_id] = YouTubeVideo(
            video_id=video_id,
            channel_id=snippet.get("channelId", "") or "",
            channel_title=snippet.get("channelTitle", "") or "",
            title=snippet.get("title", "") or "",
            description=snippet.get("description", "") or "",
            published_at=snippet.get("publishedAt", "") or "",
            url=f"https://www.youtube.com/watch?v={video_id}",
            view_count=_to_int(statistics.get("viewCount")),
            like_count=_to_int(statistics.get("likeCount")),
            comment_count=_to_int(statistics.get("commentCount")),
        )

    ordered_videos: list[YouTubeVideo] = []

    for video_id in ordered_video_ids:
        video = mapped.get(video_id)
        if video:
            ordered_videos.append(video)

    return ordered_videos