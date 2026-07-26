"""Licence validator — classify and enforce allowed licences."""

from __future__ import annotations

from docforge.core.document import ALLOWED_LICENCES, ImageCandidate, LicenceType
from docforge.images.base import ImageLicenceError
from docforge.logging.setup import get_logger

logger = get_logger(__name__)


def validate_licence(candidate: ImageCandidate) -> None:
    """Raise ImageLicenceError if the candidate's licence is not permitted.

    Logs a warning for UNKNOWN licences before raising.
    """
    if candidate.licence == LicenceType.UNKNOWN:
        logger.warning(
            "licence_unverified",
            url=candidate.url,
            provider=candidate.provider,
        )

    if candidate.licence not in ALLOWED_LICENCES:
        raise ImageLicenceError(
            url=candidate.url,
            reported=candidate.licence.value,
            actual=candidate.licence.value,
        )


def classify(raw_licence: str) -> LicenceType:
    """Classify a raw licence string to a LicenceType."""
    lower = raw_licence.lower().strip()
    if not lower:
        return LicenceType.UNKNOWN
    if "public domain" in lower or lower == "pd":
        return LicenceType.PUBLIC_DOMAIN
    if "cc0" in lower or "cc-zero" in lower:
        return LicenceType.CC0
    if "cc-by-sa" in lower or "cc by-sa" in lower:
        return LicenceType.CC_BY_SA
    if "cc-by" in lower or "cc by" in lower:
        return LicenceType.CC_BY
    if any(t in lower for t in ("all rights reserved", "getty", "shutterstock", "no derivatives")):
        return LicenceType.UNSUPPORTED
    return LicenceType.UNKNOWN


def filter_allowed(candidates: list[ImageCandidate]) -> list[ImageCandidate]:
    allowed = [c for c in candidates if c.licence in ALLOWED_LICENCES]
    rejected = len(candidates) - len(allowed)
    if rejected:
        logger.debug("licence_filtered_out", count=rejected)
    return allowed
