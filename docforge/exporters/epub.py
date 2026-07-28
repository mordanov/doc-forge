"""EPUB exporter — converts SemanticModel to EPUB 3 via ebooklib."""

from __future__ import annotations

import html
from pathlib import Path

from docforge.core.document import (
    Chapter,
    Heading,
    ImagePlaceholder,
    Paragraph,
    SemanticModel,
    Table,
)
from docforge.logging.setup import get_logger

logger = get_logger(__name__)


def _h(text: str) -> str:
    return html.escape(text or "")


def _chapter_html(chapter: Chapter) -> str:
    parts: list[str] = []
    parts.append(f"<h{chapter.heading_level}>{_h(chapter.title)}</h{chapter.heading_level}>")

    for el in chapter.elements:
        if isinstance(el, Heading):
            level = min(el.level + 1, 6)
            parts.append(f"<h{level}>{_h(el.text)}</h{level}>")
        elif isinstance(el, Paragraph):
            if el.text.strip():
                parts.append(f"<p>{_h(el.text)}</p>")
        elif isinstance(el, Table):
            parts.append("<table>")
            for r_idx, row in enumerate(el.rows):
                parts.append("<tr>")
                tag = "th" if r_idx == 0 else "td"
                for cell in row.cells:
                    text = " ".join(p.text for p in cell.content)
                    parts.append(f"<{tag}>{_h(text)}</{tag}>")
                parts.append("</tr>")
            parts.append("</table>")
        elif isinstance(el, ImagePlaceholder):
            hint = _h(el.context_hint or el.placeholder_text.split("\n")[0])
            parts.append(f"<p><em>[Image: {hint}]</em></p>")

    return "\n".join(parts)


def export(
    model: SemanticModel,
    output_path: Path,
    title: str = "",
    language: str = "en",
) -> Path:
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError:
        raise RuntimeError(
            "ebooklib is required for EPUB export. Install with: pip install EbookLib"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc_title = title or (model.chapters[0].title if model.chapters else "Document")

    book = epub.EpubBook()
    book.set_identifier(f"docforge-{output_path.stem}")
    book.set_title(doc_title)
    book.set_language(language)

    css = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=b"body{font-family:serif;margin:2rem;}h1,h2,h3{margin-top:1.5rem;}p{line-height:1.6;}",
    )
    book.add_item(css)

    chapters_epub = []
    for i, chapter in enumerate(model.chapters):
        item = epub.EpubHtml(
            title=chapter.title,
            file_name=f"chapter_{i:03d}.xhtml",
            lang=language,
        )
        item.content = f"""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{_h(chapter.title)}</title><link rel="stylesheet" href="style.css"/></head>
<body>{_chapter_html(chapter)}</body>
</html>"""
        item.add_item(css)
        book.add_item(item)
        chapters_epub.append(item)

    book.toc = tuple(epub.Link(ch.file_name, ch.title, ch.id) for ch in chapters_epub)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters_epub

    epub.write_epub(str(output_path), book)
    logger.info("epub_exported", path=str(output_path), size=output_path.stat().st_size)
    return output_path
