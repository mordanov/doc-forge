"""Unit tests for document/loader.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from docforge.document.loader import DocumentLoadError, load_document


def test_load_document_file_not_found(tmp_path):
    with pytest.raises(DocumentLoadError, match="File not found"):
        load_document(tmp_path / "missing.docx")


def test_load_document_wrong_extension(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("hello")
    with pytest.raises(DocumentLoadError, match=r"Expected \.docx"):
        load_document(f)


def test_load_document_corrupt_file(tmp_path):
    f = tmp_path / "broken.docx"
    f.write_bytes(b"not a docx")
    with pytest.raises(DocumentLoadError, match="Cannot open"):
        load_document(f)


def test_load_document_returns_document():
    example = Path(__file__).parents[2] / "examples" / "sample-guide.docx"
    if not example.exists():
        pytest.skip("sample-guide.docx not available")
    doc = load_document(example)
    assert doc.id  # has a UUID
    assert doc.source_path == example.resolve()
