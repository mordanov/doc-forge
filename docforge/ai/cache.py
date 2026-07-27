"""AI response cache — SHA-256 keyed filesystem cache for RenderingDecision objects."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from docforge.cache.base import CacheBase
from docforge.core.rendering import RenderingDecision
from docforge.logging.setup import get_logger

logger = get_logger(__name__)


class AIResponseCache:
    def __init__(self, backend: CacheBase) -> None:
        self._backend = backend

    def _make_key(self, prompt_id: str, prompt_version: str, context: dict[str, Any]) -> str:
        payload = json.dumps(
            {"prompt_id": prompt_id, "prompt_version": prompt_version, "context": context},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(
        self, prompt_id: str, prompt_version: str, context: dict[str, Any]
    ) -> RenderingDecision | None:
        key = self._make_key(prompt_id, prompt_version, context)
        raw = self._backend.get(key)
        if raw is None:
            return None
        try:
            data = json.loads(raw.decode())
            decision = RenderingDecision(**data)
            logger.debug("ai_cache_hit", key=key[:16])
            return decision
        except Exception as exc:
            logger.warning("ai_cache_corrupt", key=key[:16], error=str(exc))
            self._backend.delete(key)
            return None

    def put(
        self,
        prompt_id: str,
        prompt_version: str,
        context: dict[str, Any],
        decision: RenderingDecision,
    ) -> None:
        key = self._make_key(prompt_id, prompt_version, context)
        data = decision.model_dump()
        self._backend.put(
            key,
            json.dumps(data, default=str).encode(),
            metadata={"prompt_id": prompt_id, "prompt_version": prompt_version},
        )
        logger.debug("ai_cache_put", key=key[:16])
