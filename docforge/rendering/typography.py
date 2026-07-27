"""Language-specific typography rules."""

from __future__ import annotations

_QUOTE_MARKS: dict[str, tuple[str, str]] = {
    "en": ("“", "”"),
    "ru": ("«", "»"),
    "de": ("„", "“"),
    "fr": ("« ", " »"),
    "es": ("«", "»"),
}

_DATE_FORMATS: dict[str, str] = {
    "en": "%B %d, %Y",
    "ru": "%d %B %Y г.",
    "de": "%d. %B %Y",
    "fr": "%d %B %Y",
    "es": "%d de %B de %Y",
}


def get_quote_marks(language: str) -> tuple[str, str]:
    lang = language.lower().split("-")[0]
    return _QUOTE_MARKS.get(lang, _QUOTE_MARKS["en"])


def get_date_format(language: str) -> str:
    lang = language.lower().split("-")[0]
    return _DATE_FORMATS.get(lang, _DATE_FORMATS["en"])


def apply_typography(text: str, language: str) -> str:
    """Apply language-specific typographic rules to a text string."""
    open_q, close_q = get_quote_marks(language)
    result = text.replace('"', open_q, 1)
    if open_q in result:
        result = result.replace('"', close_q, 1)
    return result
