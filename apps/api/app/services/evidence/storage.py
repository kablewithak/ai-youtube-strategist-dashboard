from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.evidence import ScreenshotEvidence


ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
}


def ensure_upload_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[3]
    upload_dir = base_dir / settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _safe_extension(filename: str, mime_type: str) -> str:
    lowered = filename.lower()

    if lowered.endswith(".png"):
        return ".png"
    if lowered.endswith(".jpg") or lowered.endswith(".jpeg"):
        return ".jpg"
    if lowered.endswith(".webp"):
        return ".webp"
    if lowered.endswith(".heic"):
        return ".heic"
    if lowered.endswith(".heif"):
        return ".heif"

    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/jpeg":
        return ".jpg"
    if mime_type == "image/webp":
        return ".webp"
    if mime_type == "image/heic":
        return ".heic"
    if mime_type == "image/heif":
        return ".heif"

    return ".bin"


async def save_screenshot_upload(upload: UploadFile) -> ScreenshotEvidence:
    mime_type = upload.content_type or "application/octet-stream"

    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError(
            "Unsupported image type. Use PNG, JPEG, WEBP, HEIC, or HEIF screenshots."
        )

    upload_dir = ensure_upload_dir()
    extension = _safe_extension(upload.filename or "upload", mime_type)
    stored_filename = f"{uuid4().hex}{extension}"
    destination = upload_dir / stored_filename

    size_bytes = 0

    with destination.open("wb") as output_file:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size_bytes += len(chunk)
            output_file.write(chunk)

    return ScreenshotEvidence(
        original_filename=upload.filename or stored_filename,
        stored_filename=stored_filename,
        local_path=str(destination),
        mime_type=mime_type,
        size_bytes=size_bytes,
    )