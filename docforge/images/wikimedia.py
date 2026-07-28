"""Wikimedia Commons image provider."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import httpx

from docforge.core.document import ALLOWED_LICENCES, ImageCandidate, LicenceType, Orientation
from docforge.images.base import ImageDownloadError, ImageProvider
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_API_URL = "https://commons.wikimedia.org/w/api.php"
_THUMBNAIL_URL = "https://commons.wikimedia.org/wiki/Special:FilePath"
_RATE_LIMIT_INTERVAL = 1.0  # seconds between requests

# Wikimedia API requires a descriptive User-Agent to avoid 403 blocks.
# See: https://www.mediawiki.org/wiki/API:Etiquette
_HEADERS = {
    "User-Agent": "DocForge/1.0 (https://github.com/docforge/docforge; docforge@example.com) httpx/0.27",
}


_LICENCE_MAP: dict[str, LicenceType] = {
    "public domain": LicenceType.PUBLIC_DOMAIN,
    "cc0": LicenceType.CC0,
    "cc-zero": LicenceType.CC0,
    "cc by": LicenceType.CC_BY,
    "cc-by": LicenceType.CC_BY,
    "cc by-sa": LicenceType.CC_BY_SA,
    "cc-by-sa": LicenceType.CC_BY_SA,
}


def _map_licence(raw: str) -> LicenceType:
    lower = raw.lower().strip()
    for key, value in _LICENCE_MAP.items():
        if key in lower:
            return value
    return LicenceType.UNKNOWN


class WikimediaProvider(ImageProvider):
    def __init__(self) -> None:
        self._last_request: float = 0.0

    @property
    def provider_id(self) -> str:
        return "wikimedia"

    @property
    def capabilities(self) -> list[str]:
        return ["image_search", "image_download"]

    async def _rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < _RATE_LIMIT_INTERVAL:
            await asyncio.sleep(_RATE_LIMIT_INTERVAL - elapsed)
        self._last_request = time.monotonic()

    async def search(
        self,
        query: str,
        max_results: int = 10,
        orientation: str | None = None,
    ) -> list[ImageCandidate]:
        await self._rate_limit()
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",  # File namespace
            "gsrsearch": query,
            "gsrlimit": str(min(max_results * 2, 20)),  # over-fetch to allow filtering
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata|mime",
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=10.0, headers=_HEADERS) as client:
            try:
                response = await client.get(_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as exc:
                logger.warning("wikimedia_search_failed", query=query, error=str(exc))
                return []

        pages = (data.get("query") or {}).get("pages") or {}
        candidates: list[ImageCandidate] = []

        for page in pages.values():
            imageinfo = (page.get("imageinfo") or [{}])[0]
            if not imageinfo:
                continue

            mime = imageinfo.get("mime", "")
            if not mime.startswith("image/"):
                continue

            ext_meta = imageinfo.get("extmetadata") or {}
            licence_raw = (ext_meta.get("LicenseShortName") or {}).get("value", "") or (
                ext_meta.get("License") or {}
            ).get("value", "")
            licence = _map_licence(licence_raw)

            if licence not in ALLOWED_LICENCES:
                continue

            width = imageinfo.get("width", 0)
            height = imageinfo.get("height", 0)
            candidate_orientation = _calc_orientation(width, height)

            if orientation and candidate_orientation.value != orientation:
                continue

            author = (ext_meta.get("Artist") or {}).get("value", "") or None
            title = page.get("title", "").removeprefix("File:")

            candidates.append(
                ImageCandidate(
                    provider=self.provider_id,
                    url=imageinfo.get("url", ""),
                    title=title,
                    author=_strip_html(author) if author else None,
                    licence=licence,
                    width=width,
                    height=height,
                    orientation=candidate_orientation,
                    source_page=imageinfo.get("descriptionurl"),
                )
            )

            if len(candidates) >= max_results:
                break

        return candidates

    async def download(
        self,
        candidate: ImageCandidate,
        target_path: Path,
        max_width: int = 1920,
        max_height: int = 1080,
    ) -> Path:
        if not candidate.url:
            raise ImageDownloadError(self.provider_id, candidate.url, "No URL")

        await self._rate_limit()
        target_path.parent.mkdir(parents=True, exist_ok=True)

        referer = candidate.source_page or "https://commons.wikimedia.org/"
        dl_headers = {**_HEADERS, "Referer": referer}
        async with httpx.AsyncClient(
            timeout=30.0, follow_redirects=True, headers=dl_headers
        ) as client:
            try:
                async with client.stream("GET", candidate.url) as response:
                    response.raise_for_status()
                    with open(target_path, "wb") as f:
                        async for chunk in response.aiter_bytes(8192):
                            f.write(chunk)
            except httpx.HTTPError as exc:
                raise ImageDownloadError(self.provider_id, candidate.url, str(exc)) from exc

        return target_path

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=_HEADERS) as client:
                r = await client.get(
                    _API_URL, params={"action": "query", "format": "json", "meta": "siteinfo"}
                )
                return r.status_code == 200
        except Exception:
            return False


def _calc_orientation(width: int, height: int) -> Orientation:
    if width > height:
        return Orientation.LANDSCAPE
    if height > width:
        return Orientation.PORTRAIT
    return Orientation.SQUARE


def _strip_html(text: str) -> str:
    import re

    return re.sub(r"<[^>]+>", "", text).strip()
