"""Full render pipeline — Loader → Analyser → AI → Images → Theme → Renderer → Validator → Exporter."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path

from docforge.ai.base import AIContext
from docforge.ai.cache import AIResponseCache
from docforge.ai.defaults import DefaultRenderingDecision
from docforge.ai.prompts.loader import load_prompt
from docforge.cache.filesystem import FilesystemCache
from docforge.core.document import ImagePlaceholder
from docforge.core.rendering import PhotoLayout, RenderingDecision, RenderStage
from docforge.document.analyser import analyse
from docforge.document.loader import load_document
from docforge.exporters import docx as docx_exporter
from docforge.images.cache import ImageCache
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
    offline_mode: bool = False,
    image_sources: list[str] | None = None,
    image_cache_dir: Path | None = None,
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
        model, issues = analyse(input_path, extra_placeholder_patterns=[])
        logger.info(
            "pipeline_analysed",
            chapters=len(model.chapters),
            warnings=len(issues),
        )
        for issue in issues:
            report.add_warning(f"[{issue.code}] {issue.message}")

        # Stage 3: Validate layout before rendering
        on_stage(RenderStage.VALIDATION, 20, "Validating layout")
        validation = validate_layout(model)
        logger.info(
            "pipeline_validated",
            warnings=len(validation.warnings),
            errors=len(validation.errors),
        )
        for w in validation.warnings:
            report.add_warning(f"[{w.code}] {w.message}")
        for e in validation.errors:
            report.add_warning(f"[ERROR:{e.code}] {e.message}")

        # Stage 4: AI processing
        chapter_count = len(model.chapters)
        if ai_provider is None:
            logger.warning(
                "pipeline_ai_skipped",
                reason="no ai_provider",
                hint="Set OPENAI_API_KEY env var to enable AI processing",
                chapters=chapter_count,
            )
        else:
            logger.info(
                "pipeline_ai_start",
                provider=getattr(ai_provider, "provider_id", type(ai_provider).__name__),
                model=ai_model,
                chapters=chapter_count,
            )

        on_stage(RenderStage.AI_PROCESSING, 40, "Generating layout decisions")
        decisions: dict[str, RenderingDecision] = {}
        for i, chapter in enumerate(model.chapters):
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
                    logger.debug(
                        "pipeline_ai_cache_hit",
                        chapter=chapter.title,
                        index=i + 1,
                        total=chapter_count,
                    )
                    decisions[chapter.id] = cached
                else:
                    logger.debug(
                        "pipeline_ai_calling",
                        chapter=chapter.title,
                        index=i + 1,
                        total=chapter_count,
                    )
                    on_stage(
                        RenderStage.AI_PROCESSING,
                        40 + int(30 * i / chapter_count),
                        f"AI: chapter {i + 1}/{chapter_count} — {chapter.title}",
                    )
                    try:
                        prompt = load_prompt("editorial_v1")
                        decision = await ai_provider.generate(
                            prompt, context, model=ai_model, creativity=creativity
                        )
                        logger.info(
                            "pipeline_ai_decision",
                            chapter=chapter.title,
                            index=i + 1,
                            total=chapter_count,
                            style=getattr(decision, "chapter_style", "?"),
                        )
                        decisions[chapter.id] = decision
                        if ai_cache:
                            ai_cache.put("editorial_v1", "1.0.0", context.fields, decision)
                    except Exception as exc:
                        logger.warning(
                            "pipeline_ai_chapter_failed",
                            chapter=chapter.title,
                            error=str(exc),
                        )
                        report.add_recovered_error(
                            f"AI failed for chapter '{chapter.title}': {exc}"
                        )
                        decisions[chapter.id] = DefaultRenderingDecision.for_chapter(chapter.id)
            else:
                decisions[chapter.id] = DefaultRenderingDecision.for_chapter(chapter.id)

        if ai_provider is not None:
            logger.info("pipeline_ai_done", chapters_processed=len(decisions))

        # Stage 5: Image search & download
        images_dir = output_path.parent / f"{output_path.stem}_images"
        fetched_images: dict[int, Path] = {}

        # Build image providers from config
        enabled_sources = set(image_sources or ["wikimedia"])
        providers = []
        if not offline_mode:
            if "wikimedia" in enabled_sources:
                from docforge.images.wikimedia import WikimediaProvider
                providers.append(WikimediaProvider())
            if "pexels" in enabled_sources:
                import os as _os
                pexels_key = _os.getenv("PEXELS_API_KEY", "").strip()
                if pexels_key:
                    from docforge.images.pexels import PexelsProvider
                    providers.append(PexelsProvider(pexels_key))
                else:
                    logger.warning("pexels_key_missing", hint="Set PEXELS_API_KEY to enable Pexels")
            if "unsplash" in enabled_sources:
                import os as _os
                unsplash_key = _os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
                if unsplash_key:
                    from docforge.images.unsplash import UnsplashProvider
                    providers.append(UnsplashProvider(unsplash_key))
                else:
                    logger.warning("unsplash_key_missing", hint="Set UNSPLASH_ACCESS_KEY to enable Unsplash")

        # Set up image cache
        img_cache: ImageCache | None = None
        if image_cache_dir:
            img_cache = ImageCache(FilesystemCache(image_cache_dir, bucket="images"))

        try:
            placeholders = [
                (chapter, el)
                for chapter in model.chapters
                for el in chapter.elements
                if isinstance(el, ImagePlaceholder)
            ]
            total_placeholders = len(placeholders)
            if total_placeholders > 0:
                on_stage(RenderStage.SEARCHING_IMAGES, 72, f"Searching images (0/{total_placeholders})")
                logger.info("pipeline_image_search_start", total=total_placeholders, offline=offline_mode)

                # Map placeholder id → ImageCandidate for download stage
                candidate_map: dict[int, object] = {}

                for idx, (chapter, placeholder) in enumerate(placeholders):
                    decision = decisions.get(chapter.id)
                    if decision and decision.photo_layout == PhotoLayout.NONE:
                        continue
                    query = placeholder.context_hint or placeholder.placeholder_text.split("\n")[0]
                    on_stage(
                        RenderStage.SEARCHING_IMAGES,
                        72 + int(3 * idx / total_placeholders),
                        f"Searching images ({idx + 1}/{total_placeholders})",
                    )
                    for provider in providers:
                        try:
                            candidates = await provider.search(query, max_results=1)
                            if candidates:
                                candidate_map[id(placeholder)] = candidates[0]
                                break
                        except Exception as exc:
                            logger.warning("pipeline_image_search_failed", query=query, provider=provider.provider_id, error=str(exc))

                logger.info("pipeline_image_search_done", found=len(candidate_map), total=total_placeholders)

                if candidate_map:
                    on_stage(RenderStage.DOWNLOADING_IMAGES, 75, f"Downloading images (0/{len(candidate_map)})")
                    images_dir.mkdir(parents=True, exist_ok=True)
                    downloaded: dict[int, Path] = {}
                    for dl_idx, (ph_id, candidate) in enumerate(candidate_map.items()):
                        on_stage(
                            RenderStage.DOWNLOADING_IMAGES,
                            75 + int(5 * dl_idx / len(candidate_map)),
                            f"Downloading images ({dl_idx + 1}/{len(candidate_map)})",
                        )
                        try:
                            # Check image cache first
                            cached = img_cache.get(candidate, 1200, 900) if img_cache else None  # type: ignore[arg-type]
                            opt_path = images_dir / f"img_{dl_idx:03d}.jpg"
                            if cached:
                                opt_path.write_bytes(cached[0])
                                logger.debug("image_cache_hit", index=dl_idx)
                            else:
                                ext = candidate.url.rsplit(".", 1)[-1].split("?")[0].lower() or "jpg"  # type: ignore[union-attr]
                                raw_path = images_dir / f"img_{dl_idx:03d}_raw.{ext}"
                                # Find the provider that found this candidate
                                provider_id = getattr(candidate, "provider", "wikimedia")
                                dl_provider = next((p for p in providers if p.provider_id == provider_id), providers[0] if providers else None)
                                if dl_provider:
                                    await dl_provider.download(candidate, raw_path)  # type: ignore[arg-type]
                                from docforge.images.optimiser import optimise
                                optimise(raw_path, opt_path, max_width=1200, max_height=900)
                                raw_path.unlink(missing_ok=True)
                                if img_cache and opt_path.exists():
                                    img_cache.put(candidate, 1200, 900, opt_path.read_bytes())  # type: ignore[arg-type]
                            downloaded[int(ph_id)] = opt_path
                            report.add_image_attribution(candidate)  # type: ignore[arg-type]
                        except Exception as exc:
                            logger.warning("pipeline_image_download_failed", error=str(exc))
                    fetched_images = downloaded  # type: ignore[assignment]
                    logger.info("pipeline_image_download_done", downloaded=len(downloaded))
        except Exception as exc:
            logger.warning("pipeline_image_stage_failed", error=str(exc))

        # Stage 6: Render
        on_stage(RenderStage.RENDERING, 80, "Rendering document")
        theme = load_theme(template)
        engine = RenderingEngine(theme)
        doc = engine.render(
            model, decisions, output_path, language=language,
            images=fetched_images,
            image_attributions=report.image_attributions,
        )

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
        logger.info("pipeline_finished", output=str(output_path), warnings=len(report.warnings))

    except Exception as exc:
        report.fatal_failure = str(exc)
        report.finish()
        logger.error("pipeline_failed", error=str(exc), exc_info=True)

    return report
