"""Pexels image provider."""

from __future__ import annotations

from pathlib import Path

import httpx

from docforge.core.document import ImageCandidate, LicenceType, Orientation
from docforge.images.base import ImageDownloadError, ImageProvider
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_API_URL = "https://api.pexels.com/v1"


class PexelsProvider(ImageProvider):
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("PEXELS_API_KEY is required")
        self._api_key = api_key

    @property
    def provider_id(self) -> str:
        return "pexels"

    @property
    def capabilities(self) -> list[str]:
        return ["image_search", "image_download"]

    async def search(
        self,
        query: str,
        max_results: int = 10,
        orientation: str | None = None,
    ) -> list[ImageCandidate]:
        params: dict = {
            "query": query,
            "per_page": str(min(max_results, 80)),
        }
        if orientation:
            params["orientation"] = orientation

        async with httpx.AsyncClient(
            headers={"Authorization": self._api_key}, timeout=10.0
        ) as client:
            try:
                r = await client.get(f"{_API_URL}/search", params=params)
                r.raise_for_status()
                data = r.json()
            except httpx.HTTPError as exc:
                logger.warning("pexels_search_failed", query=query, error=str(exc))
                return []

        candidates = []
        for photo in data.get("photos", [])[:max_results]:
            w = photo.get("width", 0)
            h = photo.get("height", 0)
            src = photo.get("src", {})
            candidates.append(
                ImageCandidate(
                    provider=self.provider_id,
                    url=src.get("large2x") or src.get("original", ""),
                    title=photo.get("alt") or query,
                    author=photo.get("photographer"),
                    licence=LicenceType.CC_BY,  # Pexels requires attribution
                    width=w,
                    height=h,
                    orientation=_calc_orientation(w, h),
                    source_page=photo.get("url"),
                )
            )
        return candidates

    async def download(
        self,
        candidate: ImageCandidate,
        target_path: Path,
        max_width: int = 1920,
        max_height: int = 1080,
    ) -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                async with client.stream("GET", candidate.url) as r:
                    r.raise_for_status()
                    with open(target_path, "wb") as f:
                        async for chunk in r.aiter_bytes(8192):
                            f.write(chunk)
            except httpx.HTTPError as exc:
                raise ImageDownloadError(self.provider_id, candidate.url, str(exc)) from exc
        return target_path

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(
                headers={"Authorization": self._api_key}, timeout=5.0
            ) as client:
                r = await client.get(
                    f"{_API_URL}/search", params={"query": "test", "per_page": "1"}
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
