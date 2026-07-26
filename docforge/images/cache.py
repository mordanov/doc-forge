"""Image cache — filesystem-backed, keyed by SHA-256 of (url, checksum, dimensions, licence)."""

from __future__ import annotations

import hashlib
import json

from docforge.cache.base import CacheBase
from docforge.core.document import ImageCandidate
from docforge.logging.setup import get_logger

logger = get_logger(__name__)


class ImageCache:
    def __init__(self, backend: CacheBase) -> None:
        self._backend = backend

    def _make_key(
        self,
        candidate: ImageCandidate,
        width: int,
        height: int,
    ) -> str:
        payload = json.dumps(
            {
                "url": candidate.url,
                "licence": candidate.licence.value,
                "width": width,
                "height": height,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(self, candidate: ImageCandidate, width: int, height: int) -> tuple[bytes, dict] | None:
        key = self._make_key(candidate, width, height)
        data = self._backend.get(key)
        if data is None:
            return None
        meta = self._backend.get_metadata(key) or {}
        logger.debug("image_cache_hit", key=key[:16])
        return data, meta

    def put(
        self,
        candidate: ImageCandidate,
        width: int,
        height: int,
        image_bytes: bytes,
    ) -> None:
        key = self._make_key(candidate, width, height)
        meta = {
            "url": candidate.url,
            "provider": candidate.provider,
            "title": candidate.title,
            "author": candidate.author,
            "licence": candidate.licence.value,
            "source_page": candidate.source_page,
            "width": width,
            "height": height,
        }
        self._backend.put(key, image_bytes, metadata=meta)
        logger.debug("image_cache_put", key=key[:16])
