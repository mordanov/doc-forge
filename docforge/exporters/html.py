"""HTML exporter — converts SemanticModel to a standalone HTML file."""

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

_CSS = """
body { font-family: Georgia, serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #1a1a1a; }
h1 { font-size: 2rem; margin-top: 2rem; }
h2 { font-size: 1.5rem; margin-top: 1.5rem; }
h3 { font-size: 1.25rem; }
p { margin: 0.75rem 0; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }
th { background: #f5f5f5; }
figure { margin: 1.5rem 0; text-align: center; }
figcaption { font-size: 0.85rem; color: #555; font-style: italic; margin-top: 0.25rem; }
.placeholder { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 1rem; border-radius: 4px; }
"""


def _h(text: str) -> str:
    return html.escape(text or "")


def _render_chapter(chapter: Chapter) -> str:
    parts: list[str] = []
    parts.append(f'<section id="{_h(chapter.id)}">')
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
            parts.append(
                f'<figure><div class="placeholder">[Image: {hint}]</div><figcaption>{hint}</figcaption></figure>'
            )

    parts.append("</section>")
    return "\n".join(parts)


def export(
    model: SemanticModel,
    output_path: Path,
    title: str = "",
    language: str = "en",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc_title = title or (model.chapters[0].title if model.chapters else "Document")
    body = "\n".join(_render_chapter(ch) for ch in model.chapters)

    html_content = f"""<!DOCTYPE html>
<html lang="{_h(language)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_h(doc_title)}</title>
<style>{_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

    output_path.write_text(html_content, encoding="utf-8")
    logger.info("html_exported", path=str(output_path), size=output_path.stat().st_size)
    return output_path
