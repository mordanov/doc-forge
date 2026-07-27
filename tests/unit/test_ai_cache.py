"""Unit tests for AIResponseCache."""

from pathlib import Path

import pytest

from docforge.ai.cache import AIResponseCache
from docforge.cache.filesystem import FilesystemCache
from docforge.core.rendering import ChapterStyle, PageBalance, PhotoLayout, RenderingDecision


@pytest.fixture
def ai_cache(tmp_path: Path) -> AIResponseCache:
    backend = FilesystemCache(tmp_path, bucket="ai")
    return AIResponseCache(backend)


def _decision(chapter_id: str = "ch1") -> RenderingDecision:
    return RenderingDecision(
        chapter_id=chapter_id,
        chapter_style=ChapterStyle.FEATURE,
        photo_layout=PhotoLayout.TWO_COLUMN,
        page_balance=PageBalance.SPACIOUS,
    )


def test_cache_miss(ai_cache: AIResponseCache):
    assert ai_cache.get("p1", "v1", {"key": "val"}) is None


def test_put_and_get(ai_cache: AIResponseCache):
    decision = _decision()
    ai_cache.put("p1", "v1", {"chapter": "intro"}, decision)
    result = ai_cache.get("p1", "v1", {"chapter": "intro"})
    assert result is not None
    assert result.chapter_id == "ch1"
    assert result.chapter_style == ChapterStyle.FEATURE


def test_different_context_is_miss(ai_cache: AIResponseCache):
    decision = _decision()
    ai_cache.put("p1", "v1", {"chapter": "intro"}, decision)
    assert ai_cache.get("p1", "v1", {"chapter": "conclusion"}) is None


def test_different_version_is_miss(ai_cache: AIResponseCache):
    decision = _decision()
    ai_cache.put("p1", "v1", {"chapter": "intro"}, decision)
    assert ai_cache.get("p1", "v2", {"chapter": "intro"}) is None


def test_corrupt_cache_entry_returns_none(ai_cache: AIResponseCache, tmp_path: Path):
    # Put a valid entry then corrupt the stored bytes
    decision = _decision()
    ai_cache.put("p1", "v1", {"x": 1}, decision)

    key = ai_cache._make_key("p1", "v1", {"x": 1})
    data_path = tmp_path / "ai" / key[:2] / key
    data_path.write_bytes(b"not-json-at-all")

    assert ai_cache.get("p1", "v1", {"x": 1}) is None
