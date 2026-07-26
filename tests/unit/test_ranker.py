"""Unit tests for image candidate ranker."""

from docforge.core.document import ImageCandidate, LicenceType, Orientation
from docforge.images.ranker import rank, score


def _make(licence=LicenceType.CC_BY, width=1920, height=1080, relevance=0.8) -> ImageCandidate:
    return ImageCandidate(
        provider="test",
        url="http://example.com/img.jpg",
        title="Test",
        licence=licence,
        width=width,
        height=height,
        orientation=Orientation.LANDSCAPE,
        relevance=relevance,
    )


def test_rank_filters_disallowed():
    candidates = [
        _make(licence=LicenceType.CC_BY),
        _make(licence=LicenceType.UNKNOWN),
        _make(licence=LicenceType.UNSUPPORTED),
    ]
    ranked = rank(candidates)
    assert len(ranked) == 1
    assert ranked[0].licence == LicenceType.CC_BY


def test_rank_public_domain_scores_higher():
    pd = _make(licence=LicenceType.PUBLIC_DOMAIN, relevance=0.5)
    cc_by = _make(licence=LicenceType.CC_BY, relevance=0.5)
    ranked = rank([cc_by, pd])
    assert ranked[0].licence == LicenceType.PUBLIC_DOMAIN


def test_rank_higher_resolution_scores_higher():
    hd = _make(licence=LicenceType.CC0, width=1920, height=1080)
    low = _make(licence=LicenceType.CC0, width=400, height=300)
    ranked = rank([low, hd])
    assert ranked[0].width == 1920


def test_score_lower_for_unknown_licence():
    unknown = _make(licence=LicenceType.UNKNOWN)
    pd = _make(licence=LicenceType.PUBLIC_DOMAIN)
    # UNKNOWN licence scores lower than PUBLIC_DOMAIN
    assert score(unknown) < score(pd)


def test_rank_empty():
    assert rank([]) == []
