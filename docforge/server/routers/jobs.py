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

    queue = get_job_queue(Path(request.app.state.db_path))
    await queue.submit(job_req)

    return {"job_id": job_id, "status": "QUEUED"}


@router.get("/{job_id}")
async def get_job(job_id: str, request: Request) -> dict:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    job = store.get_job(conn, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(job)


@router.get("/{job_id}/download/{fmt}")
async def download_job(job_id: str, fmt: str, request: Request) -> FileResponse:
    _auth_check(request)

    if fmt != "docx":
        raise HTTPException(status_code=400, detail="Only 'docx' format is supported in v1")

    conn = store.get_connection(Path(request.app.state.db_path))
    job = store.get_job(conn, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "COMPLETED":
        raise HTTPException(
            status_code=409, detail=f"Job is not completed (status: {job['status']})"
        )

    output_paths = json.loads(job.get("output_paths", "[]"))
    if not output_paths:
        raise HTTPException(status_code=404, detail="No output files for this job")

    path = Path(output_paths[0])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Output file not found on disk")

    return FileResponse(
        path=str(path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{job_id}.docx",
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, request: Request) -> Response:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    job = store.get_job(conn, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "RUNNING":
        raise HTTPException(status_code=409, detail="Cannot delete a running job")

    store.delete_job(conn, job_id)
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

    return {
        "estimated_rendering_seconds": max(10, stats.chapter_count * 5),
        "estimated_ai_tokens": ai_tokens,
        "estimated_ai_requests": ai_requests,
        "estimated_page_count": stats.page_count_estimate,
        "image_placeholder_count": stats.placeholder_count,
        "validation_summary": {"warnings": [], "errors": []},
        "licence_summary": {
            "providers_available": ["wikimedia"],
            "expected_licensed": stats.placeholder_count,
            "expected_unlicensed": 0,
        },
    }
