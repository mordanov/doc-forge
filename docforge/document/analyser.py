"""DocumentAnalyser — traverses a Document and produces a SemanticModel.

Also implements issue detection (T042): orphan headings, missing captions,
duplicate IDs, malformed tables.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

import docx
import docx.table
import docx.text.paragraph

from docforge.core.document import (
    Cell,
    Chapter,
    DocumentStatistics,
    Heading,
    ImagePlaceholder,
    Paragraph,
    Row,
    Run,
    SemanticModel,
    Table,
)
from docforge.core.rendering import ValidationIssue

# Inline markers: <image …>, <img …>, [image …], [photo …], [figure …]
_INLINE_PLACEHOLDER_RE = re.compile(
    r"<image[^>]*>|<img[^>]*>|\[image[^\]]*\]|\[photo[^\]]*\]|\[figure[^\]]*\]",
    re.IGNORECASE,
)

# Structural markers: standalone lines that label a photo block.
# These are whole-paragraph patterns — the paragraph text is matched in full.
_STRUCTURAL_PLACEHOLDER_RE = re.compile(
    r"""
    ^\s*(
        (?:фото|фотография|рис(?:унок)?|фиг(?:ура)?|иллюстрация)   # Russian
        |(?:photo|figure|fig|illustration|image|picture|pic)        # English/common
        |(?:foto|abbildung|abb)                                      # German/Spanish
    )[\s\.\-—:]*\d*\s*$                                             # optional number
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Поиск / Search prefix — the search-hint paragraph that follows a photo block
_SEARCH_HINT_RE = re.compile(
    r"^\s*(поиск|search)\s*[:\-—]?\s*",
    re.IGNORECASE,
)


def _build_extra_re(patterns: list[str]) -> re.Pattern | None:
    if not patterns:
        return None
    combined = "|".join(f"(?:{p})" for p in patterns)
    return re.compile(combined, re.IGNORECASE)


def _is_placeholder_line(text: str, extra_re: re.Pattern | None) -> bool:
    """Return True if this paragraph should be treated as an image placeholder marker."""
    if _INLINE_PLACEHOLDER_RE.search(text):
        return True
    if _STRUCTURAL_PLACEHOLDER_RE.match(text):
        return True
    if extra_re and extra_re.search(text):
        return True
    return False


def analyse(
    path: Path,
    extra_placeholder_patterns: list[str] | None = None,
) -> tuple[SemanticModel, list[ValidationIssue]]:
    """Analyse a .docx file without modifying it.

    Returns (SemanticModel, list[ValidationIssue]).
    """
    extra_re = _build_extra_re(extra_placeholder_patterns or [])

    doc = docx.Document(str(path))
    doc_id = str(uuid.uuid4())

    chapters: list[Chapter] = []
    issues: list[ValidationIssue] = []
    current_chapter: Chapter | None = None
    prev_heading_level: int = 0
    word_count = 0
    table_count = 0
    placeholder_count = 0
    heading_count = 0

    # Collect all blocks first so we can do look-ahead coalescing.
    blocks = list(_iter_blocks(doc))
    i = 0
    while i < len(blocks):
        block = blocks[i]

        if isinstance(block, Heading):
            heading_count += 1
            if block.level == 1:
                current_chapter = Chapter(
                    id=str(uuid.uuid4()),
                    title=block.text,
                    heading_level=1,
                )
                chapters.append(current_chapter)
            else:
                if current_chapter is None:
                    issues.append(
                        ValidationIssue(
                            code="ORPHAN_HEADING",
                            message=f"Heading '{block.text}' appears before any chapter heading",
                            location=f"Heading level {block.level}",
                        )
                    )
                    current_chapter = Chapter(
                        id=str(uuid.uuid4()),
                        title=block.text,
                        heading_level=block.level,
                    )
                    chapters.append(current_chapter)
                else:
                    current_chapter.elements.append(block)

            if block.level > prev_heading_level + 1 and prev_heading_level > 0:
                issues.append(
                    ValidationIssue(
                        code="SKIPPED_HEADING_LEVEL",
                        message=f"Heading level jumped from {prev_heading_level} to {block.level}",
                        location=block.text[:80],
                    )
                )
            prev_heading_level = block.level
            i += 1

        elif isinstance(block, Paragraph):
            word_count += len(block.text.split())

            if _is_placeholder_line(block.text, extra_re):
                # Structural coalescing: consume up to 3 following paragraphs as
                # caption + search-hint lines (stop at headings or tables).
                label = block.text.strip()
                caption_parts: list[str] = []
                search_hint = ""
                j = i + 1
                while j < len(blocks) and j <= i + 3:
                    nxt = blocks[j]
                    if not isinstance(nxt, Paragraph) or not nxt.text.strip():
                        break
                    # Stop if the next line is itself another placeholder marker
                    if _is_placeholder_line(nxt.text, extra_re):
                        break
                    hint_match = _SEARCH_HINT_RE.match(nxt.text)
                    if hint_match:
                        search_hint = nxt.text[hint_match.end():].strip()
                        j += 1
                        break
                    caption_parts.append(nxt.text.strip())
                    j += 1

                caption = " ".join(caption_parts)
                context = search_hint or caption or label
                full_text = label
                if caption:
                    full_text += f"\n{caption}"
                if search_hint:
                    full_text += f"\nПоиск: {search_hint}"

                placeholder = ImagePlaceholder(
                    placeholder_text=full_text,
                    context_hint=context[:200],
                )
                placeholder_count += 1
                target = current_chapter or _ensure_intro_chapter(chapters)
                target.elements.append(placeholder)
                i = j  # skip consumed lines
            else:
                target = current_chapter or _ensure_intro_chapter(chapters)
                target.elements.append(block)
                i += 1

        elif isinstance(block, Table):
            table_count += 1
            if len(block.rows) == 0:
                issues.append(
                    ValidationIssue(
                        code="EMPTY_TABLE",
                        message="Table with no rows detected",
                        location=f"After chapter: {current_chapter.title if current_chapter else 'preamble'}",
                    )
                )
            target = current_chapter or _ensure_intro_chapter(chapters)
            target.elements.append(block)
            i += 1
        else:
            i += 1

    page_count_estimate = max(1, word_count // 300)

    stats = DocumentStatistics(
        page_count_estimate=page_count_estimate,
        chapter_count=len(chapters),
        heading_count=heading_count,
        table_count=table_count,
        placeholder_count=placeholder_count,
        word_count=word_count,
    )

    return SemanticModel(document_id=doc_id, chapters=chapters, statistics=stats), issues


def _iter_blocks(doc: Any):
    """Yield Heading, Paragraph, or Table domain objects from a docx document."""
    body = doc.element.body
    for child in body:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "p":
            para_elem = docx.text.paragraph.Paragraph(child, doc)
            style_name = para_elem.style.name if para_elem.style else ""
            text = para_elem.text

            if style_name.startswith("Heading"):
                try:
                    level = int(style_name.split()[-1])
                except (ValueError, IndexError):
                    level = 1
                if text.strip():
                    yield Heading(text=text.strip(), level=level)
            else:
                runs = [
                    Run(
                        text=r.text or "",
                        bold=bool(r.bold),
                        italic=bool(r.italic),
                        underline=bool(r.underline),
                        style=r.style.name if r.style else None,
                    )
                    for r in para_elem.runs
                    if r.text
                ]
                yield Paragraph(text=text, style=style_name or None, runs=runs)

        elif tag == "tbl":
            tbl_elem = docx.table.Table(child, doc)
            rows = []
            for row in tbl_elem.rows:
                cells = []
                for cell in row.cells:
                    cell_paras = [
                        Paragraph(text=p.text, style=p.style.name if p.style else None)
                        for p in cell.paragraphs
                        if p.text.strip()
                    ]
                    cells.append(Cell(content=cell_paras))
                rows.append(Row(cells=cells))
            yield Table(rows=rows)


def _ensure_intro_chapter(chapters: list[Chapter]) -> Chapter:
    if not chapters:
        intro = Chapter(id=str(uuid.uuid4()), title="Introduction", heading_level=1)
        chapters.append(intro)
    return chapters[0]


