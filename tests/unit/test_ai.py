"""Unit tests for AI defaults and cache."""

from docforge.ai.defaults import DefaultRenderingDecision
from docforge.core.rendering import ChapterStyle, PageBalance, PhotoLayout, RenderingDecision


def test_default_rendering_decision_is_conservative():
    d = DefaultRenderingDecision.for_chapter("ch-1")
    assert isinstance(d, RenderingDecision)
    assert d.chapter_id == "ch-1"
    assert d.chapter_style == ChapterStyle.STANDARD
    assert d.photo_layout == PhotoLayout.INLINE
    assert d.pull_quote is False
    assert d.callout is False
    assert d.page_balance == PageBalance.BALANCED
    assert d.sidebar.enabled is False


def test_default_rendering_decision_different_chapters():
    d1 = DefaultRenderingDecision.for_chapter("a")
    d2 = DefaultRenderingDecision.for_chapter("b")
    assert d1.chapter_id == "a"
    assert d2.chapter_id == "b"
    assert d1.chapter_style == d2.chapter_style
