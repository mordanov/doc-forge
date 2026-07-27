"""Filesystem-based cache backend."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from docforge.cache.base import CacheBase


class FilesystemCache(CacheBase):
    def __init__(self, cache_dir: Path, bucket: str = "default") -> None:
        self._root = cache_dir / bucket
        self._root.mkdir(parents=True, exist_ok=True)

    def _data_path(self, key: str) -> Path:
        return self._root / key[:2] / key

    def _meta_path(self, key: str) -> Path:
        return self._root / key[:2] / f"{key}.json"

    def get(self, key: str) -> bytes | None:
        path = self._data_path(key)
        if path.exists():
            return path.read_bytes()
        return None

    def put(self, key: str, data: bytes, metadata: dict[str, Any] | None = None) -> Path:
        path = self._data_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if metadata is not None:
            self._meta_path(key).write_text(json.dumps(metadata, default=str))
        return path

    def get_metadata(self, key: str) -> dict[str, Any] | None:
        meta_path = self._meta_path(key)
        if meta_path.exists():
            return json.loads(meta_path.read_text())  # type: ignore[no-any-return]
        return None

    def exists(self, key: str) -> bool:
        return self._data_path(key).exists()

    def delete(self, key: str) -> None:
        for path in (self._data_path(key), self._meta_path(key)):
            if path.exists():
                path.unlink()

    def clear(self) -> None:
        if self._root.exists():
            shutil.rmtree(self._root)
        self._root.mkdir(parents=True, exist_ok=True)

    def stats(self) -> dict[str, Any]:
        total_size = 0
        item_count = 0
        for path in self._root.rglob("*"):
            if path.is_file() and path.suffix != ".json":
                total_size += path.stat().st_size
                item_count += 1
        return {
            "bucket": self._root.name,
            "item_count": item_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
        }
