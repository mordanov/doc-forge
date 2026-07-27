"""Core document domain models — pure Python, no I/O."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field


class LicenceType(StrEnum):
    PUBLIC_DOMAIN = "public_domain"
    CC0 = "cc0"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


ALLOWED_LICENCES: frozenset[LicenceType] = frozenset(
    {LicenceType.PUBLIC_DOMAIN, LicenceType.CC0, LicenceType.CC_BY, LicenceType.CC_BY_SA}
)


class Orientation(StrEnum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class Placement(StrEnum):
    INLINE = "inline"
    FLOAT_LEFT = "float_left"
    FLOAT_RIGHT = "float_right"
    FULL_WIDTH = "full_width"


class SidebarStyle(StrEnum):
    NONE = "none"
    MINIMAL = "minimal"
    EDITORIAL = "editorial"
    MAGAZINE = "magazine"


# ---------------------------------------------------------------------------
# Leaf elements
# ---------------------------------------------------------------------------


class Run(BaseModel):
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    style: str | None = None


class Paragraph(BaseModel):
    text: str
    style: str | None = None
    runs: list[Run] = Field(default_factory=list)


class Heading(BaseModel):
    text: str
    level: int = Field(ge=1, le=6)


class Cell(BaseModel):
    content: list[Paragraph] = Field(default_factory=list)


class Row(BaseModel):
    cells: list[Cell] = Field(default_factory=list)


class Table(BaseModel):
    rows: list[Row] = Field(default_factory=list)


class ImagePlaceholder(BaseModel):
    placeholder_text: str
    context_hint: str = ""


class DocumentMeta(BaseModel):
    author: str | None = None
    subject: str | None = None
    keywords: list[str] = Field(default_factory=list)
    created: datetime | None = None
    modified: datetime | None = None


class CachedAsset(BaseModel):
    cache_key: str
    source_url: str
    local_path: Path
    licence: LicenceType
    author: str | None = None
    title: str | None = None
    source_page: str | None = None
    width: int = 0
    height: int = 0
    file_size: int = 0
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: str = ""


class Image(BaseModel):
    asset: CachedAsset
    caption: str = ""
    placement: Placement = Placement.INLINE


class Caption(BaseModel):
    text: str
    figure_id: str


class Sidebar(BaseModel):
    style: SidebarStyle = SidebarStyle.MINIMAL
    content: list[Paragraph] = Field(default_factory=list)


class PageBreak(BaseModel):
    pass


class ImageAttribution(BaseModel):
    figure_id: str
    page_number: int | None = None
    title: str
    photographer: str | None = None
    source: str
    url: str
    licence: LicenceType
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)


class Appendix(BaseModel):
    title: str = "Image Sources"
    entries: list[ImageAttribution] = Field(default_factory=list)


class Header(BaseModel):
    text: str
    odd: bool = True


class Footer(BaseModel):
    text: str
    odd: bool = True


# Discriminated union for all element types
Element = Annotated[
    Paragraph
    | Heading
    | Table
    | ImagePlaceholder
    | Image
    | Caption
    | Sidebar
    | PageBreak
    | Header
    | Footer
    | Appendix,
    Field(discriminator=None),
]


class Chapter(BaseModel):
    id: str
    title: str
    heading_level: int = Field(default=1, ge=1, le=6)
    elements: list[
        Paragraph
        | Heading
        | Table
        | ImagePlaceholder
        | Image
        | Caption
        | Sidebar
        | PageBreak
        | Header
        | Footer
        | Appendix
    ] = Field(default_factory=list)


class DocumentStatistics(BaseModel):
    page_count_estimate: int = 0
    chapter_count: int = 0
    heading_count: int = 0
    table_count: int = 0
    placeholder_count: int = 0
    word_count: int = 0


class SemanticModel(BaseModel):
    document_id: str
    chapters: list[Chapter] = Field(default_factory=list)
    statistics: DocumentStatistics = Field(default_factory=DocumentStatistics)


class Document(BaseModel):
    id: str
    source_path: Path
    title: str = ""
    language: str = "en"
    metadata: DocumentMeta = Field(default_factory=DocumentMeta)
    sections: list[SemanticModel] = Field(default_factory=list)


class ImageCandidate(BaseModel):
    provider: str
    url: str
    title: str
    author: str | None = None
    licence: LicenceType = LicenceType.UNKNOWN
    width: int = 0
    height: int = 0
    orientation: Orientation = Orientation.LANDSCAPE
    relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    source_page: str | None = None
