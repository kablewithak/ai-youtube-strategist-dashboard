from __future__ import annotations

from urllib.parse import urlparse

from app.schemas.youtube import ParsedYouTubeChannelUrl


def parse_youtube_channel_url(url: str) -> ParsedYouTubeChannelUrl:
    raw_url = (url or "").strip()
    if not raw_url:
        raise ValueError("Channel URL is required.")

    if "://" not in raw_url:
        raw_url = f"https://{raw_url}"

    parsed = urlparse(raw_url)
    host = parsed.netloc.lower()
    path = (parsed.path or "").strip()

    if host.startswith("www."):
        host = host[4:]

    if host not in {"youtube.com", "m.youtube.com"}:
        raise ValueError("Only youtube.com channel URLs are supported for now.")

    cleaned_segments = [segment for segment in path.split("/") if segment]

    if not cleaned_segments:
        raise ValueError("Could not determine the channel identifier from the URL.")

    first = cleaned_segments[0]

    if first.startswith("@"):
        return ParsedYouTubeChannelUrl(
            source_url=url,
            identifier_type="handle",
            identifier=first[1:],
        )

    if first == "channel" and len(cleaned_segments) >= 2:
        return ParsedYouTubeChannelUrl(
            source_url=url,
            identifier_type="channel_id",
            identifier=cleaned_segments[1],
        )

    if first == "c" and len(cleaned_segments) >= 2:
        return ParsedYouTubeChannelUrl(
            source_url=url,
            identifier_type="custom_name",
            identifier=cleaned_segments[1],
        )

    if first == "user" and len(cleaned_segments) >= 2:
        return ParsedYouTubeChannelUrl(
            source_url=url,
            identifier_type="username",
            identifier=cleaned_segments[1],
        )

    raise ValueError(
        "Unsupported YouTube channel URL format. Use a handle, /channel/, /c/, or /user/ URL."
    )