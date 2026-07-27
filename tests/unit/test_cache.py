"""Unit tests for FilesystemCache and ImageCache."""

from pathlib import Path

import pytest

from docforge.cache.filesystem import FilesystemCache
from docforge.core.document import ImageCandidate, LicenceType
from docforge.images.cache import ImageCache


@pytest.fixture
def fs_cache(tmp_path: Path) -> FilesystemCache:
    return FilesystemCache(tmp_path, bucket="test")


def test_put_and_get(fs_cache: FilesystemCache):
    fs_cache.put("abc123", b"hello")
    assert fs_cache.get("abc123") == b"hello"


def test_get_missing_returns_none(fs_cache: FilesystemCache):
    assert fs_cache.get("nonexistent") is None


def test_exists(fs_cache: FilesystemCache):
    assert not fs_cache.exists("k1")
    fs_cache.put("k1", b"data")
    assert fs_cache.exists("k1")


def test_delete(fs_cache: FilesystemCache):
    fs_cache.put("k2", b"data")
    fs_cache.delete("k2")
    assert not fs_cache.exists("k2")


def test_delete_nonexistent_is_safe(fs_cache: FilesystemCache):
    fs_cache.delete("ghost")  # must not raise


def test_put_with_metadata(fs_cache: FilesystemCache):
    fs_cache.put("k3", b"payload", metadata={"source": "test"})
    meta = fs_cache.get_metadata("k3")
    assert meta is not None
    assert meta["source"] == "test"


def test_get_metadata_missing_returns_none(fs_cache: FilesystemCache):
    assert fs_cache.get_metadata("nope") is None


def test_clear(fs_cache: FilesystemCache):
    fs_cache.put("k4", b"x")
    fs_cache.clear()
    assert not fs_cache.exists("k4")


def test_stats_empty(fs_cache: FilesystemCache):
    stats = fs_cache.stats()
    assert stats["item_count"] == 0
    assert stats["total_size_bytes"] == 0


def test_stats_with_data(fs_cache: FilesystemCache):
    fs_cache.put("k5", b"1234567890")
    stats = fs_cache.stats()
    assert stats["item_count"] == 1
    assert stats["total_size_bytes"] == 10


# ---------- ImageCache ----------


def _make_candidate() -> ImageCandidate:
    return ImageCandidate(
        url="https://example.com/img.jpg",
        provider="test",
        title="Test Image",
        author="Test Author",
        licence=LicenceType.CC_BY,
        source_page="https://example.com",
    )


@pytest.fixture
def img_cache(tmp_path: Path) -> ImageCache:
    backend = FilesystemCache(tmp_path, bucket="images")
    return ImageCache(backend)


def test_image_cache_miss(img_cache: ImageCache):
    candidate = _make_candidate()
    assert img_cache.get(candidate, 800, 600) is None


def test_image_cache_put_and_get(img_cache: ImageCache):
    candidate = _make_candidate()
    img_cache.put(candidate, 800, 600, b"imgdata")
    result = img_cache.get(candidate, 800, 600)
    assert result is not None
    data, meta = result
    assert data == b"imgdata"
    assert meta["url"] == "https://example.com/img.jpg"
    assert meta["width"] == 800


def test_image_cache_different_dimensions_miss(img_cache: ImageCache):
    candidate = _make_candidate()
    img_cache.put(candidate, 800, 600, b"imgdata")
    assert img_cache.get(candidate, 1920, 1080) is None
