"""RenderingReport — collects outcomes of a render run."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RenderingReport:
    job_id: str
    input_filename: str
    output_path: str = ""
    template: str = ""
    language: str = "en"
    ai_model: str = ""
    duration_seconds: float = 0.0
    warnings: list[str] = field(default_factory=list)
    recovered_errors: list[str] = field(default_factory=list)
    skipped_operations: list[str] = field(default_factory=list)
    fatal_failure: str | None = None
    image_attributions: list[dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_recovered_error(self, message: str) -> None:
        self.recovered_errors.append(message)

    def add_skipped(self, message: str) -> None:
        self.skipped_operations.append(message)

    def add_image_attribution(self, candidate: object) -> None:
        self.image_attributions.append(
            {
                "provider": getattr(candidate, "provider", ""),
                "title": getattr(candidate, "title", ""),
                "author": getattr(candidate, "author", None),
                "url": getattr(candidate, "url", ""),
                "source_page": getattr(candidate, "source_page", None),
                "licence": str(getattr(candidate, "licence", "")),
            }
        )

    def finish(self) -> None:
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def succeeded(self) -> bool:
        return self.fatal_failure is None

    def summary(self) -> dict:
        return {
            "job_id": self.job_id,
            "input": self.input_filename,
            "output": self.output_path,
            "succeeded": self.succeeded(),
            "duration_seconds": round(self.duration_seconds, 2),
            "warnings": len(self.warnings),
            "recovered_errors": len(self.recovered_errors),
            "skipped": len(self.skipped_operations),
            "images": len(self.image_attributions),
            "fatal": self.fatal_failure,
        }
