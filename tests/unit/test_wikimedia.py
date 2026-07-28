"""Tests for the Wikimedia Commons image provider."""

import httpx
import pytest
import respx

from docforge.core.document import ImageCandidate
from docforge.images.wikimedia import WikimediaProvider, _headers


@pytest.mark.parametrize(
    ("configured", "expected"),
    [
        (None, "DocForge/1.0 (https://github.com/mordanov/doc-forge)"),
        (
            "DocForge-Test/1.0 (mailto:maintainer@example.com)",
            "DocForge-Test/1.0 (mailto:maintainer@example.com)",
        ),
        ("   ", "DocForge/1.0 (https://github.com/mordanov/doc-forge)"),
    ],
)
def test_headers_use_valid_default_or_environment(monkeypatch, configured, expected):
    if configured is None:
        monkeypatch.delenv("DOCFORGE_WIKIMEDIA_USER_AGENT", raising=False)
    else:
        monkeypatch.setenv("DOCFORGE_WIKIMEDIA_USER_AGENT", configured)

    assert _headers()["User-Agent"] == expected


@respx.mock
async def test_download_sends_configured_user_agent_and_referer(monkeypatch, tmp_path):
    url = "https://upload.wikimedia.org/wikipedia/commons/example.jpg"
    source_page = "https://commons.wikimedia.org/wiki/File:Example.jpg"
    user_agent = "DocForge-Test/1.0 (mailto:maintainer@example.com)"
    monkeypatch.setenv("DOCFORGE_WIKIMEDIA_USER_AGENT", user_agent)
    route = respx.get(url).mock(
        return_value=httpx.Response(
            200, content=b"image data", headers={"Content-Type": "image/jpeg"}
        )
    )
    candidate = ImageCandidate(
        provider="wikimedia",
        url=url,
        title="Example",
        source_page=source_page,
    )
    target = tmp_path / "example.jpg"

    result = await WikimediaProvider().download(candidate, target)

    assert result == target
    assert target.read_bytes() == b"image data"
    assert route.called
    request = route.calls.last.request
    assert request.headers["User-Agent"] == user_agent
    assert request.headers["Referer"] == source_page
