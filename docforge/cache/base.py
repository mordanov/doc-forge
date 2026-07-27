"""Cache backend abstraction."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class CacheBase(ABC):
    @abstractmethod
    def get(self, key: str) -> bytes | None:
        """Return cached bytes for key, or None if not cached."""
        ...

    @abstractmethod
    def put(self, key: str, data: bytes, metadata: dict[str, Any] | None = None) -> Path:
        """Store data under key. Returns path to stored file."""
        ...

    @abstractmethod
    def get_metadata(self, key: str) -> dict[str, Any] | None:
        """Return metadata sidecar for key, or None."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def stats(self) -> dict[str, Any]: ...
