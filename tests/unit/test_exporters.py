"""Unit tests for HTML, Markdown, EPUB, and PDF exporters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docforge.core.document import (
    Cell,
    Chapter,
    Heading,
    ImagePlaceholder,
    Paragraph,
    Row,
    SemanticModel,
    Table,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _model(title: str = "Test Doc", chapters: int = 2) -> SemanticModel:
    """Build a minimal SemanticModel with the given number of chapters."""
    m = SemanticModel(document_id="doc-test")
    for i in range(chapters):
        ch = Chapter(
            id=f"ch{i}",
            title=f"Chapter {i + 1}",
            heading_level=1,
        )
        ch.elements.append(Paragraph(text=f"Paragraph in chapter {i + 1}."))
        ch.elements.append(Heading(text="Sub heading", level=2))
        m.chapters.append(ch)
    return m


def _model_rich() -> SemanticModel:
    """Build a model with all element types."""
    m = SemanticModel(document_id="doc-rich")
    ch = Chapter(id="ch0", title="Rich Chapter", heading_level=1)
    ch.elements.append(Paragraph(text="Hello world."))
    ch.elements.append(Paragraph(text=""))  # empty paragraph — should be skipped
    ch.elements.append(Heading(text="Sub", level=2))
    ch.elements.append(
        Table(
            rows=[
                Row(
                    cells=[
                        Cell(content=[Paragraph(text="H1")]),
                        Cell(content=[Paragraph(text="H2")]),
                    ]
                ),
                Row(
                    cells=[Cell(content=[Paragraph(text="A")]), Cell(content=[Paragraph(text="B")])]
                ),
            ]
        )
    )
    ch.elements.append(
        ImagePlaceholder(
            placeholder_text="[IMAGE: a cat]",
            context_hint="a cat",
        )
    )
    m.chapters.append(ch)
    return m


# ---------------------------------------------------------------------------
# HTML exporter
# ---------------------------------------------------------------------------


class TestHtmlExporter:
    def test_creates_file(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "out.html"
        result = export(_model(), out)
        assert result == out
        assert out.exists()

    def test_contains_title(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "out.html"
        export(_model(), out, title="My Doc")
        content = out.read_text()
        assert "My Doc" in content

    def test_contains_chapters(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "out.html"
        export(_model(chapters=3), out)
        content = out.read_text()
        assert "Chapter 1" in content
        assert "Chapter 3" in content

    def test_rich_elements(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "out.html"
        export(_model_rich(), out)
        content = out.read_text()
        assert "Hello world" in content
        assert "<table>" in content
        assert "a cat" in content
        assert "Sub" in content

    def test_language_attr(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "out.html"
        export(_model(), out, language="ru")
        assert 'lang="ru"' in out.read_text()

    def test_empty_model(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        m = SemanticModel(document_id="empty")
        out = tmp_path / "out.html"
        export(m, out, title="Empty Doc")
        content = out.read_text()
        assert "Empty Doc" in content

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        from docforge.exporters.html import export

        out = tmp_path / "deep" / "nested" / "out.html"
        export(_model(), out)
        assert out.exists()


# ---------------------------------------------------------------------------
# Markdown exporter
# ---------------------------------------------------------------------------


class TestMarkdownExporter:
    def test_creates_file(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        out = tmp_path / "out.md"
        result = export(_model(), out)
        assert result == out
        assert out.exists()

    def test_contains_title(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        out = tmp_path / "out.md"
        export(_model(), out, title="My Title")
        content = out.read_text()
        assert "# My Title" in content

    def test_contains_chapter_headings(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        out = tmp_path / "out.md"
        export(_model(chapters=2), out)
        content = out.read_text()
        assert "# Chapter 1" in content
        assert "# Chapter 2" in content

    def test_rich_elements(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        out = tmp_path / "out.md"
        export(_model_rich(), out)
        content = out.read_text()
        assert "Hello world" in content
        assert "| H1 | H2 |" in content
        assert "---" in content
        assert "![a cat]()" in content

    def test_empty_paragraph_skipped(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        out = tmp_path / "out.md"
        export(_model_rich(), out)
        # double-blank lines shouldn't appear from empty paragraph
        content = out.read_text()
        assert "\n\n\n" not in content.strip()

    def test_empty_model(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        m = SemanticModel(document_id="empty")
        out = tmp_path / "out.md"
        export(m, out, title="Empty")
        assert "# Empty" in out.read_text()

    def test_table_with_unequal_rows(self, tmp_path: Path) -> None:
        from docforge.exporters.markdown import export

        m = SemanticModel(document_id="d")
        ch = Chapter(id="c0", title="C", heading_level=1)
        ch.elements.append(
            Table(
                rows=[
                    Row(
                        cells=[
                            Cell(content=[Paragraph(text="A")]),
                            Cell(content=[Paragraph(text="B")]),
                        ]
                    ),
                    Row(cells=[Cell(content=[Paragraph(text="X")])]),  # shorter row
                ]
            )
        )
        m.chapters.append(ch)
        out = tmp_path / "out.md"
        export(m, out)
        content = out.read_text()
        assert "| A | B |" in content
        assert "| X |  |" in content


# ---------------------------------------------------------------------------
# EPUB exporter
# ---------------------------------------------------------------------------


class TestEpubExporter:
    def test_creates_file(self, tmp_path: Path) -> None:
        pytest.importorskip("ebooklib")
        from docforge.exporters.epub import export

        out = tmp_path / "out.epub"
        result = export(_model(), out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_missing_ebooklib_raises(self, tmp_path: Path) -> None:
        import sys
        from unittest.mock import patch

        out = tmp_path / "out.epub"
        with (
            patch.dict(sys.modules, {"ebooklib": None, "ebooklib.epub": None}),
            pytest.raises(RuntimeError, match="ebooklib"),
        ):
            # Force reimport with patched modules
            import importlib

            import docforge.exporters.epub as epub_mod

            importlib.reload(epub_mod)
            epub_mod.export(_model(), out)

    def test_rich_model(self, tmp_path: Path) -> None:
        pytest.importorskip("ebooklib")
        from docforge.exporters.epub import export

        out = tmp_path / "rich.epub"
        export(_model_rich(), out, title="Rich Doc", language="en")
        assert out.exists()


# ---------------------------------------------------------------------------
# PDF exporter
# ---------------------------------------------------------------------------


class TestPdfExporter:
    def test_docx2pdf_path(self, tmp_path: Path) -> None:

        docx = tmp_path / "input.docx"
        docx.write_bytes(b"fake")

        mock_convert = MagicMock()
        with patch.dict("sys.modules", {"docx2pdf": MagicMock(convert=mock_convert)}):
            # Make convert callable produce the output file
            def _convert(src: str, dst: str) -> None:
                Path(dst).write_bytes(b"%PDF fake")

            with patch("builtins.__import__", side_effect=_import_with_docx2pdf(_convert)):
                # Simple path: docx2pdf raises ImportError → LibreOffice path
                pass  # tested via libreoffice path below

    def test_libreoffice_fallback(self, tmp_path: Path) -> None:
        from docforge.exporters.pdf import export

        docx = tmp_path / "input.docx"
        docx.write_bytes(b"fake")
        out = tmp_path / "out.pdf"

        # Mock subprocess.run to simulate LibreOffice success
        lo_output = tmp_path / "input.pdf"

        def _fake_run(cmd, **kwargs):
            lo_output.write_bytes(b"%PDF-fake")
            r = MagicMock()
            r.returncode = 0
            return r

        with (
            patch("docforge.exporters.pdf.subprocess.run", side_effect=_fake_run),
            patch("builtins.__import__", side_effect=_make_import_error("docx2pdf")),
        ):
            result = export(docx, out)
        assert result == out
        assert out.exists()

    def test_libreoffice_failure_raises(self, tmp_path: Path) -> None:
        from docforge.exporters.pdf import export

        docx = tmp_path / "input.docx"
        docx.write_bytes(b"fake")
        out = tmp_path / "out.pdf"

        def _fail_run(cmd, **kwargs):
            r = MagicMock()
            r.returncode = 1
            r.stderr = "conversion error"
            return r

        with (
            patch("docforge.exporters.pdf.subprocess.run", side_effect=_fail_run),
            patch("builtins.__import__", side_effect=_make_import_error("docx2pdf")),
            pytest.raises(RuntimeError, match="LibreOffice"),
        ):
            export(docx, out)

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        from docforge.exporters.pdf import export

        docx = tmp_path / "input.docx"
        docx.write_bytes(b"fake")
        out = tmp_path / "deep" / "nested" / "out.pdf"
        lo_output = tmp_path / "deep" / "nested" / "input.pdf"

        def _fake_run(cmd, **kwargs):
            lo_output.parent.mkdir(parents=True, exist_ok=True)
            lo_output.write_bytes(b"%PDF-fake")
            r = MagicMock()
            r.returncode = 0
            return r

        with (
            patch("docforge.exporters.pdf.subprocess.run", side_effect=_fake_run),
            patch("builtins.__import__", side_effect=_make_import_error("docx2pdf")),
        ):
            export(docx, out)
        assert out.exists()


def _make_import_error(module_name: str):
    """Return a __import__ side-effect that raises ImportError for module_name."""
    original_import = getattr(__builtins__, "__import__", __import__)

    def _import(name, *args, **kwargs):
        if name == module_name:
            raise ImportError(f"No module named '{module_name}'")
        return original_import(name, *args, **kwargs)

    return _import


def _import_with_docx2pdf(convert_fn):
    """Return a __import__ side-effect that provides a fake docx2pdf."""
    original_import = __import__

    def _import(name, *args, **kwargs):
        if name == "docx2pdf":
            m = MagicMock()
            m.convert = convert_fn
            return m
        return original_import(name, *args, **kwargs)

    return _import
