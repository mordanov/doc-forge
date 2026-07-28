"""Markdown exporter — converts SemanticModel to a Markdown file."""

from __future__ import annotations

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


def _render_chapter(chapter: Chapter) -> str:
    parts: list[str] = []
    heading_prefix = "#" * chapter.heading_level
    parts.append(f"{heading_prefix} {chapter.title}\n")

    for el in chapter.elements:
        if isinstance(el, Heading):
            prefix = "#" * min(el.level + 1, 6)
            parts.append(f"{prefix} {el.text}\n")
        elif isinstance(el, Paragraph):
            if el.text.strip():
                parts.append(f"{el.text}\n")
        elif isinstance(el, Table):
            if not el.rows:
                continue
            col_count = max(len(r.cells) for r in el.rows)
            for r_idx, row in enumerate(el.rows):
                cells = [" ".join(p.text for p in c.content) for c in row.cells]
                cells += [""] * (col_count - len(cells))
                parts.append("| " + " | ".join(cells) + " |")
                if r_idx == 0:
                    parts.append("| " + " | ".join(["---"] * col_count) + " |")
            parts.append("")
        elif isinstance(el, ImagePlaceholder):
            hint = el.context_hint or el.placeholder_text.split("\n")[0]
            parts.append(f"![{hint}]()\n*{hint}*\n")

    return "\n".join(parts)


def export(
    model: SemanticModel,
    output_path: Path,
    title: str = "",
    language: str = "en",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc_title = title or (model.chapters[0].title if model.chapters else "Document")
    content = f"# {doc_title}\n\n"
    content += "\n\n".join(_render_chapter(ch) for ch in model.chapters)

    output_path.write_text(content, encoding="utf-8")
    logger.info("markdown_exported", path=str(output_path), size=output_path.stat().st_size)
    return output_path
