"""Rendering domain models — RenderingDecision, RenderingJob, RenderEstimate."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class ChapterStyle(StrEnum):
    STANDARD = "standard"
    FEATURE = "feature"
    OPENER = "opener"


class PhotoLayout(StrEnum):
    NONE = "none"
    INLINE = "inline"
    TWO_COLUMN = "two_column"
    FULL_WIDTH = "full_width"
    MAGAZINE = "magazine"


class PageBalance(StrEnum):
    TIGHT = "tight"
    BALANCED = "balanced"
    SPACIOUS = "spacious"


class SidebarDecision(BaseModel):
    enabled: bool = False
    type: str = "minimal"


class RenderingDecision(BaseModel):
    chapter_id: str
    chapter_style: ChapterStyle = ChapterStyle.STANDARD
    photo_layout: PhotoLayout = PhotoLayout.INLINE
    sidebar: SidebarDecision = Field(default_factory=SidebarDecision)
    table_style: str = "default"
    typography_variant: str = "conservative"
    heading_colour: str | None = None
    pull_quote: bool = False
    callout: bool = False
    page_balance: PageBalance = PageBalance.BALANCED


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RenderStage(StrEnum):
    UPLOADING = "UPLOADING"
    ANALYSING = "ANALYSING"
    AI_PROCESSING = "AI_PROCESSING"
    SEARCHING_IMAGES = "SEARCHING_IMAGES"
    DOWNLOADING_IMAGES = "DOWNLOADING_IMAGES"
    RENDERING = "RENDERING"
    VALIDATION = "VALIDATION"
    EXPORT = "EXPORT"
    FINISHED = "FINISHED"


class ValidationIssue(BaseModel):
    code: str
    message: str
    location: str | None = None


class ValidationSummary(BaseModel):
    warnings: list[ValidationIssue] = Field(default_factory=list)
    errors: list[ValidationIssue] = Field(default_factory=list)


class LicenceSummary(BaseModel):
    providers_available: list[str] = Field(default_factory=list)
    expected_licensed: int = 0
    expected_unlicensed: int = 0


class RenderEstimate(BaseModel):
    estimated_rendering_seconds: int = 0
    estimated_ai_tokens: int = 0
    estimated_ai_requests: int = 0
    estimated_page_count: int = 0
    image_placeholder_count: int = 0
    validation_summary: ValidationSummary = Field(default_factory=ValidationSummary)
    licence_summary: LicenceSummary = Field(default_factory=LicenceSummary)


class RenderingJob(BaseModel):
    id: str
    project_id: str | None = None
    status: JobStatus = JobStatus.QUEUED
    stage: RenderStage = RenderStage.UPLOADING
    progress: int = Field(default=0, ge=0, le=100)
    elapsed_seconds: float = 0.0
    config_snapshot: dict = Field(default_factory=dict)
    input_filename: str = ""
    input_path: Path = Path(".")
    output_paths: list[Path] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
