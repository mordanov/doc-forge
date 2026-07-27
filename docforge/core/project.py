"""Project and UserAccount domain models."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from docforge.core.rendering import JobStatus


class UserAccount(BaseModel):
    id: int = 1
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(BaseModel):
    id: str
    name: str
    job_id: str
    input_filename: str
    config_snapshot: dict = Field(default_factory=dict)
    output_paths: list[Path] = Field(default_factory=list)
    template: str = "minimal"
    language: str = "en"
    ai_model: str = "gpt-4o"
    status: JobStatus = JobStatus.COMPLETED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
