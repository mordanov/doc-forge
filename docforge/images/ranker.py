"""Image candidate ranker — weighted scoring across licence, resolution, orientation, relevance."""

from __future__ import annotations

from docforge.core.document import ALLOWED_LICENCES, ImageCandidate, LicenceType

_DEFAULT_WEIGHTS = {
    "licence": 0.40,
    "resolution": 0.25,
    "orientation": 0.20,
    "relevance": 0.15,
}

_LICENCE_SCORE = {
    LicenceType.PUBLIC_DOMAIN: 1.0,
    LicenceType.CC0: 1.0,
    LicenceType.CC_BY: 0.8,
    LicenceType.CC_BY_SA: 0.7,
    LicenceType.UNSUPPORTED: 0.0,
    LicenceType.UNKNOWN: 0.0,
}

_MIN_RESOLUTION = 800 * 600
_IDEAL_RESOLUTION = 1920 * 1080


def _licence_score(candidate: ImageCandidate) -> float:
    return _LICENCE_SCORE.get(candidate.licence, 0.0)


def _resolution_score(candidate: ImageCandidate) -> float:
    pixels = candidate.width * candidate.height
    if pixels <= 0:
        return 0.5
    return min(1.0, pixels / _IDEAL_RESOLUTION)


def _orientation_score(candidate: ImageCandidate, preferred: str | None) -> float:
    if preferred is None:
        return 0.5
    return 1.0 if candidate.orientation.value == preferred else 0.0


def _relevance_score(candidate: ImageCandidate) -> float:
    return candidate.relevance


def score(
    candidate: ImageCandidate,
    preferred_orientation: str | None = None,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or _DEFAULT_WEIGHTS
    return (
        w["licence"] * _licence_score(candidate)
        + w["resolution"] * _resolution_score(candidate)
        + w["orientation"] * _orientation_score(candidate, preferred_orientation)
        + w["relevance"] * _relevance_score(candidate)
    )


def rank(
    candidates: list[ImageCandidate],
    preferred_orientation: str | None = None,
    weights: dict[str, float] | None = None,
) -> list[ImageCandidate]:
    """Return candidates sorted by score descending. Filters out disallowed licences."""
    allowed = [c for c in candidates if c.licence in ALLOWED_LICENCES]
    return sorted(
        allowed,
        key=lambda c: score(c, preferred_orientation, weights),
        reverse=True,
    )
