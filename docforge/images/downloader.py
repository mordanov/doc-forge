"""Parallel async image downloader."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from docforge.core.document import ImageCandidate
from docforge.images.base import ImageDownloadError
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/tiff"}


async def download_image(
    candidate: ImageCandidate,
    target_path: Path,
    max_retries: int = 3,
) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    provider = candidate.provider
    url = candidate.url

    for attempt in range(1, max_retries + 1):
        try:
            async with (
                httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client,
                client.stream("GET", url) as response,
            ):
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                mime = content_type.split(";")[0].strip()
                if mime not in _ALLOWED_MIME:
                    raise ImageDownloadError(provider, url, f"Unsupported MIME type: {mime}")

                size = 0
                with open(target_path, "wb") as f:
                    async for chunk in response.aiter_bytes(8192):
                        size += len(chunk)
                        if size > _MAX_SIZE_BYTES:
                            raise ImageDownloadError(provider, url, "File exceeds size limit")
                        f.write(chunk)

            return target_path

        except ImageDownloadError:
            raise
        except httpx.HTTPError as exc:
            logger.warning(
                "image_download_attempt_failed",
                url=url,
                attempt=attempt,
                error=str(exc),
            )
            if attempt == max_retries:
                raise ImageDownloadError(provider, url, str(exc)) from exc
            await asyncio.sleep(2 ** (attempt - 1))

    raise ImageDownloadError(provider, url, "Unknown download failure")


async def download_all(
    candidates: list[ImageCandidate],
    target_dir: Path,
    max_retries: int = 3,
) -> list[Path | None]:
    async def _download_one(candidate: ImageCandidate, idx: int) -> Path | None:
        ext = candidate.url.rsplit(".", 1)[-1].split("?")[0].lower() or "jpg"
        target = target_dir / f"image_{idx:03d}.{ext}"
        try:
            return await download_image(candidate, target, max_retries=max_retries)
        except ImageDownloadError as exc:
            logger.warning("image_download_skipped", url=candidate.url, reason=str(exc))
            return None

    tasks = [_download_one(c, i) for i, c in enumerate(candidates)]
    return list(await asyncio.gather(*tasks))
