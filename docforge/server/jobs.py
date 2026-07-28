"""Async job queue — asyncio.Queue + background worker for rendering jobs."""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from docforge.core.pipeline import render_pipeline
from docforge.core.rendering import RenderStage
from docforge.logging.setup import get_logger
from docforge.server import store

logger = get_logger(__name__)


@dataclass
class JobRequest:
    job_id: str
    input_path: Path
    output_dir: Path
    config: dict = field(default_factory=dict)
    template: str = "minimal"
    language: str = "en"
    ai_model: str = "gpt-4o"
    creativity: int = 5


class JobQueue:
    def __init__(self, db_url: str) -> None:
        self._queue: asyncio.Queue[JobRequest] = asyncio.Queue()
        self._db_url = db_url
        self._worker_task: asyncio.Task | None = None
        self._active_jobs: set[str] = set()

    def start(self) -> None:
        self._worker_task = asyncio.create_task(self._worker(), name="job-worker")

    def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()

    async def submit(self, request: JobRequest) -> str:
        conn = store.get_connection(self._db_url)
        try:
            store.insert_job(
                conn,
                request.job_id,
                request.input_path.name,
                str(request.input_path),
                request.config,
            )
        finally:
            conn.close()
        await self._queue.put(request)
        logger.info("job_submitted", job_id=request.job_id)
        return request.job_id

    async def cancel(self, job_id: str) -> bool:
        if job_id in self._active_jobs:
            return False
        conn = store.get_connection(self._db_url)
        try:
            store.update_job_status(conn, job_id, "CANCELLED", "FINISHED")
        finally:
            conn.close()
        return True

    async def _worker(self) -> None:
        logger.info("job_worker_started")
        while True:
            request = await self._queue.get()
            self._active_jobs.add(request.job_id)
            start_time = time.monotonic()

            try:
                conn = store.get_connection(self._db_url)
                try:
                    store.update_job_status(
                        conn, request.job_id, "RUNNING", "ANALYSING", progress=5
                    )
                finally:
                    conn.close()

                output_path = request.output_dir / f"{request.job_id}.docx"
                request.output_dir.mkdir(parents=True, exist_ok=True)

                def on_stage(
                    stage: RenderStage,
                    progress: int,
                    message: str,
                    _db_url: str = self._db_url,
                    _job_id: str = request.job_id,
                    _t0: float = start_time,
                ) -> None:
                    c = store.get_connection(_db_url)
                    try:
                        store.update_job_status(
                            c,
                            _job_id,
                            "RUNNING",
                            stage.value,
                            progress=progress,
                            elapsed=time.monotonic() - _t0,
                            message=message,
                        )
                    finally:
                        c.close()

                ai_provider = None
                openai_key = os.getenv("OPENAI_API_KEY", "").strip()
                if openai_key:
                    from docforge.ai.openai_adapter import OpenAIAdapter

                    ai_provider = OpenAIAdapter(api_key=openai_key)
                else:
                    logger.warning("openai_key_missing", hint="Set OPENAI_API_KEY to enable AI")

                cfg = request.config or {}
                report = await render_pipeline(
                    input_path=request.input_path,
                    output_path=output_path,
                    template=request.template,
                    language=request.language,
                    ai_provider=ai_provider,
                    ai_model=request.ai_model,
                    creativity=request.creativity,
                    on_stage=on_stage,
                    offline_mode=bool(cfg.get("offlineMode", False)),
                    image_sources=cfg.get("imageSources") or ["wikimedia"],
                )

                elapsed = time.monotonic() - start_time
                conn = store.get_connection(self._db_url)
                try:
                    if report.succeeded():
                        store.update_job_status(
                            conn,
                            request.job_id,
                            "COMPLETED",
                            "FINISHED",
                            progress=100,
                            elapsed=elapsed,
                            output_paths=[str(output_path)],
                            warnings=report.warnings,
                        )
                        project_name = Path(request.input_path.name).stem
                        store.insert_project(
                            conn,
                            name=project_name,
                            job_id=request.job_id,
                            input_filename=request.input_path.name,
                            config=request.config,
                            output_paths=[str(output_path)],
                            template=request.template,
                            language=request.language,
                            ai_model=request.ai_model,
                        )
                        logger.info("job_completed", job_id=request.job_id, elapsed=elapsed)
                    else:
                        store.update_job_status(
                            conn,
                            request.job_id,
                            "FAILED",
                            "FINISHED",
                            elapsed=elapsed,
                            error=report.fatal_failure,
                            warnings=report.warnings,
                        )
                        logger.error(
                            "job_failed", job_id=request.job_id, error=report.fatal_failure
                        )
                finally:
                    conn.close()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                elapsed = time.monotonic() - start_time
                conn = store.get_connection(self._db_url)
                try:
                    store.update_job_status(
                        conn,
                        request.job_id,
                        "FAILED",
                        "FINISHED",
                        elapsed=elapsed,
                        error=str(exc),
                    )
                finally:
                    conn.close()
                logger.error("job_exception", job_id=request.job_id, error=str(exc))
            finally:
                self._active_jobs.discard(request.job_id)
                self._queue.task_done()


_queue_instance: JobQueue | None = None


def get_job_queue(db_url: str) -> JobQueue:
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = JobQueue(db_url)
    return _queue_instance
