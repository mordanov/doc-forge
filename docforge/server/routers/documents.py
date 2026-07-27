"""Documents router — upload and analysis endpoints."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from docforge.document.analyser import analyse
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


def _upload_dir(request: Request) -> Path:
    return Path(request.app.state.upload_dir)


def _require_auth(request: Request):
    from docforge.server.auth import make_auth_dependency

    return make_auth_dependency(request.app.state.secret_key)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
) -> dict:
    _auth_check(request)

    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    doc_id = str(uuid.uuid4())
    upload_dir = Path(request.app.state.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"{doc_id}.docx"

    size = 0
    with open(dest, "wb") as f:
        while chunk := await file.read(8192):
            size += len(chunk)
            if size > _MAX_UPLOAD_BYTES:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")
            f.write(chunk)

    logger.info("document_uploaded", doc_id=doc_id, filename=file.filename, size=size)
    return {"id": doc_id, "filename": file.filename, "size": size}


@router.post("/{doc_id}/analyse")
async def analyse_document(doc_id: str, request: Request) -> dict:
    _auth_check(request)

    upload_dir = Path(request.app.state.upload_dir)
    path = upload_dir / f"{doc_id}.docx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    model, issues = analyse(path)
    stats = model.statistics

    return {
        "document_id": doc_id,
        "statistics": {
            "chapters": stats.chapter_count,
            "headings": stats.heading_count,
            "tables": stats.table_count,
            "image_placeholders": stats.placeholder_count,
            "words": stats.word_count,
            "estimated_pages": stats.page_count_estimate,
        },
        "issues": [{"code": i.code, "message": i.message, "location": i.location} for i in issues],
    }


def _auth_check(request: Request) -> None:
    from docforge.server.auth import decode_token

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.removeprefix("Bearer ").strip()
    decode_token(token, request.app.state.secret_key)
