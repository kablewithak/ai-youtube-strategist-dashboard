from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import settings


class YouTubeApiError(Exception):
    pass


class YouTubeApiClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.youtube_api_key
        self.base_url = (base_url or settings.youtube_api_base_url).rstrip("/")

        if not self.api_key:
            raise YouTubeApiError(
                "YOUTUBE_API_KEY is missing. Add it to apps/api/.env and restart the backend."
            )

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        final_params = {**params, "key": self.api_key}
        query = urlencode(final_params, doseq=True)
        url = f"{self.base_url}/{path}?{query}"

        request = Request(url, method="GET")

        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise YouTubeApiError(
                f"YouTube API request failed with status {exc.code}: {body}"
            ) from exc
        except URLError as exc:
            raise YouTubeApiError(f"Could not reach the YouTube API: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise YouTubeApiError("YouTube API returned invalid JSON.") from exc

    def channels_list(self, part: str, **filters: Any) -> dict[str, Any]:
        return self._request("channels", {"part": part, **filters})

    def search_list(self, part: str, **params: Any) -> dict[str, Any]:
        return self._request("search", {"part": part, **params})

    def playlist_items_list(self, part: str, **params: Any) -> dict[str, Any]:
        return self._request("playlistItems", {"part": part, **params})

    def videos_list(self, part: str, **params: Any) -> dict[str, Any]:
        return self._request("videos", {"part": part, **params})

    def comment_threads_list(self, part: str, **params: Any) -> dict[str, Any]:
        return self._request("commentThreads", {"part": part, **params})