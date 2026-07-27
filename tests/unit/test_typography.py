"""Unit tests for language-specific typography utilities."""

from docforge.rendering.typography import apply_typography, get_date_format, get_quote_marks


def test_english_quotes():
    open_q, close_q = get_quote_marks("en")
    assert open_q == "“"
    assert close_q == "”"


def test_russian_quotes():
    open_q, close_q = get_quote_marks("ru")
    assert open_q == "«"
    assert close_q == "»"


def test_unknown_language_falls_back_to_english():
    open_q, _close_q = get_quote_marks("zz")
    assert open_q == "“"


def test_language_tag_normalised():
    # "en-GB" → "en"
    open_q, _ = get_quote_marks("en-GB")
    assert open_q == "“"


def test_date_format_english():
    fmt = get_date_format("en")
    assert "%Y" in fmt


def test_date_format_russian():
    fmt = get_date_format("ru")
    assert "г." in fmt


def test_date_format_fallback():
    fmt = get_date_format("zz")
    assert fmt == get_date_format("en")


def test_apply_typography_replaces_quotes():
    result = apply_typography('"Hello"', "en")
    assert "“" in result or "”" in result


def test_apply_typography_no_quotes_unchanged():
    result = apply_typography("No quotes here", "en")
    assert result == "No quotes here"
