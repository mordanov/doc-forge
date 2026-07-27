"""Full render pipeline — Loader → Analyser → AI → Images → Theme → Renderer → Validator → Exporter."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path

from docforge.ai.base import AIContext
from docforge.ai.cache import AIResponseCache
from docforge.ai.defaults import DefaultRenderingDecision
from docforge.ai.prompts.loader import load_prompt
from docforge.core.rendering import RenderingDecision, RenderStage
from docforge.document.analyser import analyse
from docforge.document.loader import load_document
from docforge.exporters import docx as docx_exporter
from docforge.logging.setup import get_logger
from docforge.rendering.engine import RenderingEngine
from docforge.rendering.layout_validator import validate as validate_layout
from docforge.rendering.report import RenderingReport
from docforge.templates.engine import load_theme

logger = get_logger(__name__)

StageCallback = Callable[[RenderStage, int, str], None]


def _noop(*_) -> None:
    pass


async def render_pipeline(
    input_path: Path,
    output_path: Path,
    template: str = "minimal",
    language: str = "en",
    ai_provider=None,
    ai_model: str = "gpt-4o",
    creativity: int = 5,
    ai_cache: AIResponseCache | None = None,
    on_stage: StageCallback = _noop,
) -> RenderingReport:
    job_id = str(uuid.uuid4())
    report = RenderingReport(
        job_id=job_id,
        input_filename=input_path.name,
        output_path=str(output_path),
        template=template,
        language=language,
        ai_model=ai_model,
    )

    try:
        # Stage 1: Load
        on_stage(RenderStage.UPLOADING, 5, "Loading document")
        document = load_document(input_path)
        logger.info("pipeline_loaded", title=document.title)

        # Stage 2: Analyse
        on_stage(RenderStage.ANALYSING, 15, "Analysing document structure")
        model, issues = analyse(input_path)
        for issue in issues:
            report.add_warning(f"[{issue.code}] {issue.message}")

        # Stage 3: Validate layout before rendering
        on_stage(RenderStage.VALIDATION, 20, "Validating layout")
        validation = validate_layout(model)
        for w in validation.warnings:
            report.add_warning(f"[{w.code}] {w.message}")
        for e in validation.errors:
            report.add_warning(f"[ERROR:{e.code}] {e.message}")

        # Stage 4: AI processing
        on_stage(RenderStage.AI_PROCESSING, 40, "Generating layout decisions")
        decisions: dict[str, RenderingDecision] = {}
        for chapter in model.chapters:
            context = AIContext(
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                nearby_text="",
                placeholder_count=sum(
                    1 for e in chapter.elements if hasattr(e, "placeholder_text")
                ),
                template_name=template,
                language=language,
                chapter_word_count=sum(
                    len((getattr(e, "text", "") or "").split()) for e in chapter.elements
                ),
                has_tables=any(hasattr(e, "rows") for e in chapter.elements),
            )

            if ai_provider is not None:
                cached = None
                if ai_cache is not None:
                    cached = ai_cache.get("editorial_v1", "1.0.0", context.fields)
                if cached:
                    decisions[chapter.id] = cached
                else:
                    try:
                        prompt = load_prompt("editorial_v1")
                        decision = await ai_provider.generate(
                            prompt, context, model=ai_model, creativity=creativity
                        )
                        decisions[chapter.id] = decision
                        if ai_cache:
                            ai_cache.put("editorial_v1", "1.0.0", context.fields, decision)
                    except Exception as exc:
                        report.add_recovered_error(
                            f"AI failed for chapter '{chapter.title}': {exc}"
                        )
                        decisions[chapter.id] = DefaultRenderingDecision.for_chapter(chapter.id)
            else:
                decisions[chapter.id] = DefaultRenderingDecision.for_chapter(chapter.id)

        # Stage 5: Render
        on_stage(RenderStage.RENDERING, 70, "Rendering document")
        theme = load_theme(template)
        engine = RenderingEngine(theme)
        doc = engine.render(model, decisions, output_path, language=language)

        # Stage 6: Export with metadata
        on_stage(RenderStage.EXPORT, 90, "Exporting DOCX")
        docx_exporter.export(
            doc,
            output_path,
            title=document.title,
            language=language,
            template=template,
        )

        on_stage(RenderStage.FINISHED, 100, "Done")
        report.finish()

    except Exception as exc:
        report.fatal_failure = str(exc)
        report.finish()
        logger.error("pipeline_failed", error=str(exc))

    return report
