"""Unit tests for licence validator."""

import pytest

from docforge.core.document import ImageCandidate, LicenceType
from docforge.images.base import ImageLicenceError
from docforge.images.licence import classify, filter_allowed, validate_licence


def _candidate(licence: LicenceType) -> ImageCandidate:
    return ImageCandidate(
        provider="test", url="http://example.com/img.jpg", title="Test", licence=licence
    )


def test_validate_licence_allowed():
    for lt in (LicenceType.PUBLIC_DOMAIN, LicenceType.CC0, LicenceType.CC_BY, LicenceType.CC_BY_SA):
        validate_licence(_candidate(lt))  # should not raise


def test_validate_licence_unknown_raises():
    with pytest.raises(ImageLicenceError):
        validate_licence(_candidate(LicenceType.UNKNOWN))


def test_validate_licence_unsupported_raises():
    with pytest.raises(ImageLicenceError):
        validate_licence(_candidate(LicenceType.UNSUPPORTED))


def test_classify_public_domain():
    assert classify("Public Domain") == LicenceType.PUBLIC_DOMAIN


def test_classify_cc0():
    assert classify("CC0 1.0") == LicenceType.CC0


def test_classify_cc_by():
    assert classify("CC BY 4.0") == LicenceType.CC_BY


def test_classify_cc_by_sa():
    assert classify("CC BY-SA 3.0") == LicenceType.CC_BY_SA


def test_classify_unknown():
    assert classify("proprietary license") == LicenceType.UNKNOWN


def test_classify_empty():
    assert classify("") == LicenceType.UNKNOWN


def test_filter_allowed_removes_disallowed():
    candidates = [
        _candidate(LicenceType.CC_BY),
        _candidate(LicenceType.UNKNOWN),
        _candidate(LicenceType.UNSUPPORTED),
        _candidate(LicenceType.PUBLIC_DOMAIN),
    ]
    allowed = filter_allowed(candidates)
    assert len(allowed) == 2
    assert all(c.licence in (LicenceType.CC_BY, LicenceType.PUBLIC_DOMAIN) for c in allowed)
