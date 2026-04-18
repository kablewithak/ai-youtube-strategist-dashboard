from __future__ import annotations

from app.schemas.youtube import ParsedYouTubeChannelUrl, YouTubeChannel
from app.services.youtube.client import YouTubeApiClient


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_thumbnail_urls(thumbnails: dict) -> dict[str, str]:
    results: dict[str, str] = {}

    for key, value in thumbnails.items():
        url = value.get("url")
        if url:
            results[key] = url

    return results


def _map_channel_item(item: dict) -> YouTubeChannel:
    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})
    statistics = item.get("statistics", {})
    related_playlists = content_details.get("relatedPlaylists", {})

    return YouTubeChannel(
        channel_id=item.get("id", ""),
        title=snippet.get("title", ""),
        description=snippet.get("description", "") or "",
        custom_url=snippet.get("customUrl", "") or "",
        published_at=snippet.get("publishedAt", "") or "",
        uploads_playlist_id=related_playlists.get("uploads", "") or "",
        subscriber_count=_to_int(statistics.get("subscriberCount")),
        video_count=_to_int(statistics.get("videoCount")),
        view_count=_to_int(statistics.get("viewCount")),
        thumbnails=_extract_thumbnail_urls(snippet.get("thumbnails", {})),
    )


def _fetch_channel_by_id(client: YouTubeApiClient, channel_id: str) -> YouTubeChannel:
    response = client.channels_list(
        part="snippet,contentDetails,statistics",
        id=channel_id,
        maxResults=1,
    )

    items = response.get("items", [])
    if not items:
        raise ValueError("Could not resolve the YouTube channel by channel ID.")

    return _map_channel_item(items[0])


def resolve_youtube_channel(parsed: ParsedYouTubeChannelUrl) -> YouTubeChannel:
    client = YouTubeApiClient()

    if parsed.identifier_type == "channel_id":
        return _fetch_channel_by_id(client, parsed.identifier)

    if parsed.identifier_type == "handle":
        response = client.channels_list(
            part="snippet,contentDetails,statistics",
            forHandle=parsed.identifier,
            maxResults=1,
        )

        items = response.get("items", [])
        if not items:
            raise ValueError("Could not resolve the YouTube channel from the handle URL.")

        return _map_channel_item(items[0])

    if parsed.identifier_type == "username":
        response = client.channels_list(
            part="snippet,contentDetails,statistics",
            forUsername=parsed.identifier,
            maxResults=1,
        )

        items = response.get("items", [])
        if not items:
            raise ValueError("Could not resolve the YouTube channel from the username URL.")

        return _map_channel_item(items[0])

    if parsed.identifier_type == "custom_name":
        search_response = client.search_list(
            part="snippet",
            q=parsed.identifier,
            type="channel",
            maxResults=5,
        )

        items = search_response.get("items", [])
        if not items:
            raise ValueError("Could not resolve the YouTube channel from the custom URL.")

        first_item = items[0]
        snippet = first_item.get("snippet", {})
        channel_id = snippet.get("channelId")

        if not channel_id:
            raise ValueError("Could not determine a channel ID from the custom URL search result.")

        return _fetch_channel_by_id(client, channel_id)

    raise ValueError("Unsupported parsed YouTube channel identifier type.")