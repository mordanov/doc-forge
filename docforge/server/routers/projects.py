"""Projects router — list, detail, duplicate, delete."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, status

from docforge.logging.setup import get_logger
from docforge.server import store

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


def _auth_check(request: Request) -> None:
    from docforge.server.auth import decode_token

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.removeprefix("Bearer ").strip()
    decode_token(token, request.app.state.secret_key)


@router.get("")
async def list_projects(
    request: Request,
    offset: int = 0,
    limit: int = 20,
) -> list[dict]:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    return store.list_projects(conn, offset=offset, limit=limit)


@router.get("/{project_id}")
async def get_project(project_id: str, request: Request) -> dict:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    project = store.get_project(conn, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/duplicate", status_code=status.HTTP_202_ACCEPTED)
async def duplicate_project(project_id: str, request: Request) -> dict:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    project = store.get_project(conn, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    config = json.loads(project.get("config_snapshot", "{}"))
    upload_dir = Path(request.app.state.upload_dir)
    input_path = upload_dir / project["input_filename"]

    if not input_path.exists():
        raise HTTPException(status_code=409, detail="Original input file not found for duplication")

    from docforge.server.jobs import JobRequest, get_job_queue

    job_id = str(uuid.uuid4())
    output_dir = Path(request.app.state.output_dir)
    job_req = JobRequest(
        job_id=job_id,
        input_path=input_path,
        output_dir=output_dir,
        config=config,
        template=project.get("template", "minimal"),
        language=project.get("language", "en"),
        ai_model=project.get("ai_model", "gpt-4o"),
    )

    queue = get_job_queue(Path(request.app.state.db_path))
    await queue.submit(job_req)

    return {"job_id": job_id, "status": "QUEUED"}


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, request: Request) -> Response:
    _auth_check(request)
    conn = store.get_connection(Path(request.app.state.db_path))
    project = store.get_project(conn, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output_paths = json.loads(project.get("output_paths", "[]"))
    for path_str in output_paths:
        p = Path(path_str)
        if p.exists():
            p.unlink()
            logger.info("project_output_deleted", path=str(p))

    store.delete_project(conn, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
