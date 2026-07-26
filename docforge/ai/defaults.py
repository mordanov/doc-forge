"""DefaultRenderingDecision — conservative fallback when AI is unavailable."""

from __future__ import annotations

from docforge.core.rendering import (
    ChapterStyle,
    PageBalance,
    PhotoLayout,
    RenderingDecision,
    SidebarDecision,
)


class DefaultRenderingDecision:
    """Factory for a conservative RenderingDecision used when AI fails."""

    @staticmethod
    def for_chapter(chapter_id: str) -> RenderingDecision:
        return RenderingDecision(
            chapter_id=chapter_id,
            chapter_style=ChapterStyle.STANDARD,
            photo_layout=PhotoLayout.INLINE,
            sidebar=SidebarDecision(enabled=False),
            table_style="default",
            typography_variant="conservative",
            heading_colour=None,
            pull_quote=False,
            callout=False,
            page_balance=PageBalance.BALANCED,
        )
