"""Public Python API — Renderer fluent builder."""

from __future__ import annotations

import asyncio
from pathlib import Path

from docforge.core.pipeline import render_pipeline
from docforge.rendering.report import RenderingReport


class Renderer:
    """Fluent builder for rendering .docx documents.

    Example:
        report = Renderer().template("minimal").language("en").render("in.docx", "out.docx")
    """

    def __init__(self) -> None:
        self._template = "minimal"
        self._language = "en"
        self._model = "gpt-4o"
        self._creativity = 5
        self._ai_provider = None

    def template(self, name: str) -> Renderer:
        self._template = name
        return self

    def language(self, lang: str) -> Renderer:
        self._language = lang
        return self

    def model(self, model_name: str) -> Renderer:
        self._model = model_name
        return self

    def creativity(self, value: int) -> Renderer:
        if not 1 <= value <= 10:
            raise ValueError("creativity must be between 1 and 10")
        self._creativity = value
        return self

    def provider(self, ai_provider) -> Renderer:
        self._ai_provider = ai_provider
        return self

    def render(self, input_path: str | Path, output_path: str | Path) -> RenderingReport:
        """Synchronous render — blocks until complete."""
        return asyncio.run(self.arender(input_path, output_path))

    async def arender(self, input_path: str | Path, output_path: str | Path) -> RenderingReport:
        """Async render."""
        return await render_pipeline(
            input_path=Path(input_path),
            output_path=Path(output_path),
            template=self._template,
            language=self._language,
            ai_provider=self._ai_provider,
            ai_model=self._model,
            creativity=self._creativity,
        )
