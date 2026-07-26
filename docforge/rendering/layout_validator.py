"""LayoutValidator — structural checks on a SemanticModel before/after rendering."""

from __future__ import annotations

from docforge.core.document import (
    Chapter,
    Heading,
    ImagePlaceholder,
    SemanticModel,
    Table,
)
from docforge.core.rendering import ValidationIssue, ValidationSummary


def validate(model: SemanticModel) -> ValidationSummary:
    warnings: list[ValidationIssue] = []
    errors: list[ValidationIssue] = []

    prev_level = 0
    for chapter in model.chapters:
        chapter_loc = f"Chapter: {chapter.title}"

        if chapter.heading_level > prev_level + 1 and prev_level > 0:
            warnings.append(
                ValidationIssue(
                    code="HEADING_HIERARCHY_SKIP",
                    message=f"Heading level jumped from {prev_level} to {chapter.heading_level}",
                    location=chapter_loc,
                )
            )
        prev_level = chapter.heading_level

        _check_chapter(chapter, chapter_loc, warnings, errors)

    return ValidationSummary(warnings=warnings, errors=errors)


def _check_chapter(
    chapter: Chapter,
    loc: str,
    warnings: list[ValidationIssue],
    errors: list[ValidationIssue],
) -> None:
    elements = chapter.elements

    # Orphan heading: heading immediately followed by another heading with no content
    for i, elem in enumerate(elements):
        if isinstance(elem, Heading):
            next_elem = elements[i + 1] if i + 1 < len(elements) else None
            if isinstance(next_elem, Heading):
                warnings.append(
                    ValidationIssue(
                        code="ORPHAN_HEADING",
                        message=f"Heading '{elem.text}' has no content before next heading",
                        location=loc,
                    )
                )

    # Oversized placeholder check (ImagePlaceholder with very long text)
    for elem in elements:
        if isinstance(elem, ImagePlaceholder) and len(elem.placeholder_text) > 500:
            warnings.append(
                ValidationIssue(
                    code="OVERSIZED_PLACEHOLDER",
                    message="Image placeholder text exceeds 500 characters",
                    location=loc,
                )
            )

    # Empty table
    for elem in elements:
        if isinstance(elem, Table) and not elem.rows:
            errors.append(
                ValidationIssue(
                    code="EMPTY_TABLE",
                    message="Table with no rows",
                    location=loc,
                )
            )
