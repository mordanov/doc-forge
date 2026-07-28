"""Jobs router — submit, poll, download, cancel, estimate."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from docforge.logging.setup import get_logger
from docforge.server import store
from docforge.server.jobs import JobRequest, get_job_queue

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobSubmitRequest(BaseModel):
    document_id: str
    template: str = "minimal"
    language: str = "en"
    ai_model: str = "gpt-4o"
    creativity: int = 5
    config: dict = {}


class EstimateRequest(BaseModel):
    document_id: str
    template: str = "minimal"
    config: dict = {}


def _auth_check(request: Request) -> None:
    from docforge.server.auth import decode_token

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.removeprefix("Bearer ").strip()
    decode_token(token, request.app.state.secret_key)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_job(body: JobSubmitRequest, request: Request) -> dict:
    _auth_check(request)

    upload_dir = Path(request.app.state.upload_dir)
    input_path = upload_dir / f"{body.document_id}.docx"
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    job_id = str(uuid.uuid4())
    output_dir = Path(request.app.state.output_dir)
    job_req = JobRequest(
        job_id=job_id,
        input_path=input_path,
        output_dir=output_dir,
        config=body.config,
        template=body.template,
        language=body.language,
        ai_model=body.ai_model,
        creativity=body.creativity,
    )

    queue = get_job_queue(request.app.state.db_url)
    await queue.submit(job_req)

    return {"job_id": job_id, "status": "QUEUED"}


@router.get("/{job_id}")
async def get_job(job_id: str, request: Request) -> dict:
    _auth_check(request)
    conn = store.get_connection(request.app.state.db_url)
    try:
        job = store.get_job(conn, job_id)
    finally:
        conn.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(job)


_MEDIA_TYPES: dict[str, str] = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
    "html": "text/html",
    "markdown": "text/markdown",
    "epub": "application/epub+zip",
}

_SUPPORTED_FORMATS = set(_MEDIA_TYPES.keys())


@router.get("/{job_id}/download/{fmt}")
async def download_job(job_id: str, fmt: str, request: Request) -> FileResponse:
    _auth_check(request)

    if fmt not in _SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{fmt}'. Use: {', '.join(_SUPPORTED_FORMATS)}",
        )

    conn = store.get_connection(request.app.state.db_url)
    try:
        job = store.get_job(conn, job_id)
    finally:
        conn.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "COMPLETED":
        raise HTTPException(
            status_code=409, detail=f"Job is not completed (status: {job['status']})"
        )

    output_paths = json.loads(job.get("output_paths", "[]"))
    if not output_paths:
        raise HTTPException(status_code=404, detail="No output files for this job")

    docx_path = Path(output_paths[0])
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found on disk")

    stem = Path(job.get("input_filename", job_id)).stem
    output_dir = docx_path.parent

    if fmt == "docx":
        final_path = docx_path
    elif fmt == "pdf":
        final_path = output_dir / f"{job_id}.pdf"
        if not final_path.exists():
            from docforge.exporters import pdf as pdf_exporter

            pdf_exporter.export(docx_path, final_path)
    elif fmt == "html":
        final_path = output_dir / f"{job_id}.html"
        if not final_path.exists():
            from docforge.document.analyser import analyse
            from docforge.exporters import html as html_exporter

            model, _ = analyse(Path(job.get("input_path", str(docx_path))))
            html_exporter.export(model, final_path, language=job.get("language", "en"))
    elif fmt == "markdown":
        final_path = output_dir / f"{job_id}.md"
        if not final_path.exists():
            from docforge.document.analyser import analyse
            from docforge.exporters import markdown as md_exporter

            model, _ = analyse(Path(job.get("input_path", str(docx_path))))
            md_exporter.export(model, final_path, language=job.get("language", "en"))
    elif fmt == "epub":
        final_path = output_dir / f"{job_id}.epub"
        if not final_path.exists():
            from docforge.document.analyser import analyse
            from docforge.exporters import epub as epub_exporter

            model, _ = analyse(Path(job.get("input_path", str(docx_path))))
            epub_exporter.export(model, final_path, language=job.get("language", "en"))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown format: {fmt}")

    ext = "md" if fmt == "markdown" else fmt
    download_name = f"docforged-{stem}.{ext}"
    return FileResponse(
        path=str(final_path),
        media_type=_MEDIA_TYPES[fmt],
        filename=download_name,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, request: Request) -> Response:
    _auth_check(request)
    conn = store.get_connection(request.app.state.db_url)
    try:
        job = store.get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job["status"] == "RUNNING":
            raise HTTPException(status_code=409, detail="Cannot delete a running job")
        store.delete_job(conn, job_id)
    finally:
        conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/estimate")
async def estimate_job(body: EstimateRequest, request: Request) -> dict:
    _auth_check(request)

    upload_dir = Path(request.app.state.upload_dir)
    input_path = upload_dir / f"{body.document_id}.docx"
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    from docforge.document.analyser import analyse

    model, _issues = analyse(input_path)
    stats = model.statistics

    ai_requests = stats.chapter_count
    ai_tokens = ai_requests * 500

    # gpt-4o pricing: $2.50 / 1M input tokens, $10.00 / 1M output tokens
    # assume ~80% input, ~20% output
    cost_usd = round(ai_tokens * 0.8 * 2.50 / 1_000_000 + ai_tokens * 0.2 * 10.00 / 1_000_000, 4)

    # Derive structural features from config hints passed in the estimate body
    cfg = getattr(body, "config", {}) or {}
    cover_page = cfg.get("coverPage", "auto")
    toc = cfg.get("tableOfContents", "generate")
    headers_footers = cfg.get("headersFooters", "generate")

    has_cover_page = cover_page not in ("none",)
    has_toc = toc in ("generate", "update_existing")
    has_headers_footers = headers_footers in ("generate", "replace_existing")
    generated_captions = stats.placeholder_count
    generated_appendix = stats.placeholder_count > 0

    return {
        "estimated_rendering_seconds": max(10, stats.chapter_count * 5),
        "estimated_ai_tokens": ai_tokens,
        "estimated_ai_requests": ai_requests,
        "estimated_ai_cost_usd": cost_usd,
        "estimated_page_count": stats.page_count_estimate,
        "image_placeholder_count": stats.placeholder_count,
        "generated_captions": generated_captions,
        "generated_appendix": generated_appendix,
        "has_cover_page": has_cover_page,
        "has_toc": has_toc,
        "has_headers_footers": has_headers_footers,
        "validation_summary": {"warnings": [], "errors": []},
        "licence_summary": {
            "providers_available": ["wikimedia"],
            "expected_licensed": stats.placeholder_count,
            "expected_unlicensed": 0,
        },
    }
