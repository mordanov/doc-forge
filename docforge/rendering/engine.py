"""RenderingEngine — applies theme + layout decisions to a SemanticModel via python-docx."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from docforge.core.document import (
    Chapter,
    Heading,
    ImagePlaceholder,
    Paragraph,
    SemanticModel,
    Table,
)
from docforge.core.rendering import RenderingDecision
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_POINTS_PER_PT = 1


class RenderingEngine:
    def __init__(self, theme: dict) -> None:
        self._theme = theme

    def render(
        self,
        model: SemanticModel,
        decisions: dict[str, RenderingDecision],
        output_path: Path,
        language: str = "en",
    ) -> Any:
        doc = docx.Document()
        self._apply_page_setup(doc)

        self._add_cover(doc, model, language)
        self._add_toc(doc, model, language)

        for chapter in model.chapters:
            decision = decisions.get(chapter.id)
            self._render_chapter(doc, chapter, decision)

        self._add_image_sources_appendix(doc, model, language)
        self._add_headers_footers(doc, language)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        logger.info("rendering_complete", output=str(output_path))
        return doc

    def _apply_page_setup(self, doc: Any) -> None:
        spacing = self._theme.get("spacing", {})
        for section in doc.sections:
            section.top_margin = Cm(spacing.get("page_margin_top_cm", 2.54))
            section.bottom_margin = Cm(spacing.get("page_margin_bottom_cm", 2.54))
            section.left_margin = Cm(spacing.get("page_margin_left_cm", 2.54))
            section.right_margin = Cm(spacing.get("page_margin_right_cm", 2.54))

    def _add_cover(self, doc: Any, model: SemanticModel, language: str) -> None:
        palette = self._theme.get("palette", {})
        title = model.chapters[0].title if model.chapters else "Document"

        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(title)
        run.bold = True
        run.font.size = Pt(28)
        colour_hex = palette.get("primary", "#1a1a2e").lstrip("#")
        run.font.color.rgb = RGBColor(
            int(colour_hex[0:2], 16),
            int(colour_hex[2:4], 16),
            int(colour_hex[4:6], 16),
        )
        doc.add_page_break()

    def _add_toc(self, doc: Any, model: SemanticModel, language: str) -> None:
        from docforge.core.i18n import get_label

        toc_label = get_label("toc", language)
        doc.add_heading(toc_label, level=1)
        for chapter in model.chapters:
            para = doc.add_paragraph(chapter.title, style="List Bullet")
            para.paragraph_format.left_indent = Cm(0)
        doc.add_page_break()

    def _render_chapter(
        self,
        doc: Any,
        chapter: Chapter,
        decision: RenderingDecision | None,
    ) -> None:
        doc.add_heading(chapter.title, level=chapter.heading_level)

        for element in chapter.elements:
            if isinstance(element, Heading):
                doc.add_heading(element.text, level=element.level)
            elif isinstance(element, Paragraph):
                if element.text.strip():
                    p = doc.add_paragraph(element.text)
                    if element.style:
                        import contextlib

                        with contextlib.suppress(KeyError):
                            p.style = doc.styles[element.style]
            elif isinstance(element, Table):
                self._render_table(doc, element)
            elif isinstance(element, ImagePlaceholder):
                p = doc.add_paragraph(f"[Image placeholder: {element.placeholder_text}]")
                p.runs[0].italic = True

    def _render_table(self, doc: Any, table: Table) -> None:
        if not table.rows:
            return
        col_count = max(len(row.cells) for row in table.rows)
        doc_table = doc.add_table(rows=len(table.rows), cols=col_count)
        doc_table.style = "Table Grid"
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                if c_idx < col_count:
                    text = " ".join(p.text for p in cell.content)
                    doc_table.cell(r_idx, c_idx).text = text

    def _add_image_sources_appendix(self, doc: Any, model: SemanticModel, language: str) -> None:
        from docforge.core.i18n import get_label

        appendix_label = get_label("image_sources", language)
        doc.add_page_break()
        doc.add_heading(appendix_label, level=1)
        doc.add_paragraph("No images were sourced in this rendering.")

    def _add_headers_footers(self, doc: Any, language: str) -> None:
        for section in doc.sections:
            header = section.header
            if not header.paragraphs:
                header.add_paragraph()
            header.paragraphs[0].text = ""

            footer = section.footer
            if not footer.paragraphs:
                footer.add_paragraph()
            para = footer.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if not para.runs:
                para.add_run("")
