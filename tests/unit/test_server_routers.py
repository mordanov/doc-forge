"""Unit tests for all server routers using a fake app (no DB required)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from docforge.server.auth import create_token, hash_password
from docforge.server.routers import auth, documents, jobs, projects, system

SECRET = "test-secret-32-chars-minimum-key!!"
TOKEN = create_token("admin", SECRET, ttl_hours=1)
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _make_app(tmp_path: Path) -> FastAPI:
    """Build a minimal FastAPI app wired like the real one but without DB startup."""
    app = FastAPI()
    app.state.db_url = "postgresql://fake/fake"
    app.state.upload_dir = str(tmp_path / "uploads")
    app.state.output_dir = str(tmp_path / "output")
    app.state.secret_key = SECRET
    app.state.token_ttl_hours = 1
    (tmp_path / "uploads").mkdir()
    (tmp_path / "output").mkdir()
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(jobs.router)
    app.include_router(projects.router)
    app.include_router(system.router)
    return app


# ---------------------------------------------------------------------------
# system router
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/system/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_themes_endpoint(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/system/themes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_providers_endpoint(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/system/providers")
    assert r.status_code == 200
    data = r.json()
    assert "ai" in data
    assert "images" in data


# ---------------------------------------------------------------------------
# auth router
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(tmp_path):
    app = _make_app(tmp_path)
    user = {"username": "admin", "password_hash": hash_password("secret")}

    with (
        patch("docforge.server.routers.auth.store.get_connection"),
        patch("docforge.server.routers.auth.store.get_user", return_value=user),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post("/auth/login", json={"username": "admin", "password": "secret"})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(tmp_path):
    app = _make_app(tmp_path)
    user = {"username": "admin", "password_hash": hash_password("correct")}

    with (
        patch("docforge.server.routers.auth.store.get_connection"),
        patch("docforge.server.routers.auth.store.get_user", return_value=user),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_no_user_503(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.auth.store.get_connection"),
        patch("docforge.server.routers.auth.store.get_user", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post("/auth/login", json={"username": "admin", "password": "x"})
    assert r.status_code == 503


@pytest.mark.asyncio
async def test_login_wrong_username(tmp_path):
    app = _make_app(tmp_path)
    user = {"username": "admin", "password_hash": hash_password("secret")}

    with (
        patch("docforge.server.routers.auth.store.get_connection"),
        patch("docforge.server.routers.auth.store.get_user", return_value=user),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post("/auth/login", json={"username": "other", "password": "secret"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# documents router
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upload_requires_auth(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/documents/upload",
            files={"file": ("test.docx", b"data", "application/octet-stream")},
        )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_upload_rejects_non_docx(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/documents/upload",
            files={"file": ("test.txt", b"hi", "text/plain")},
            headers=AUTH,
        )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_docx_succeeds(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/documents/upload",
            files={"file": ("doc.docx", b"fake-docx-content", "application/octet-stream")},
            headers=AUTH,
        )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["filename"] == "doc.docx"


@pytest.mark.asyncio
async def test_analyse_document_not_found(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/documents/ghost-id/analyse", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_analyse_requires_auth(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/documents/ghost-id/analyse")
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# jobs router
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_job_requires_auth(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/jobs/some-id")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_job_not_found(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/jobs/missing", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_job_found(tmp_path):
    app = _make_app(tmp_path)
    job = {
        "id": "j1",
        "status": "QUEUED",
        "stage": "UPLOADING",
        "progress": 0,
        "elapsed_seconds": 0,
        "config_snapshot": "{}",
        "input_filename": "f.docx",
        "input_path": "/tmp/f.docx",
        "output_paths": "[]",
        "warnings": "[]",
        "error": None,
        "created_at": "2024",
        "started_at": None,
        "completed_at": None,
        "project_id": None,
    }

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=job),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/jobs/j1", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["id"] == "j1"


@pytest.mark.asyncio
async def test_delete_job_not_found(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.delete("/jobs/missing", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_running_job_rejected(tmp_path):
    app = _make_app(tmp_path)
    job = {"id": "j1", "status": "RUNNING"}

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=job),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.delete("/jobs/j1", headers=AUTH)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_delete_queued_job_succeeds(tmp_path):
    app = _make_app(tmp_path)
    job = {"id": "j1", "status": "QUEUED"}

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=job),
        patch("docforge.server.routers.jobs.store.delete_job", return_value=True),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.delete("/jobs/j1", headers=AUTH)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_download_job_unsupported_format(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/jobs/j1/download/pdf", headers=AUTH)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_download_job_not_found(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/jobs/ghost/download/docx", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_download_job_not_completed(tmp_path):
    app = _make_app(tmp_path)
    job = {"id": "j1", "status": "RUNNING"}

    with (
        patch("docforge.server.routers.jobs.store.get_connection"),
        patch("docforge.server.routers.jobs.store.get_job", return_value=job),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/jobs/j1/download/docx", headers=AUTH)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_submit_job_requires_auth(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/jobs", json={"document_id": "x"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_submit_job_document_not_found(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/jobs", json={"document_id": "nonexistent"}, headers=AUTH)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# projects router
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_projects_requires_auth(tmp_path):
    app = _make_app(tmp_path)
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/projects")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_projects_returns_list(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.projects.store.get_connection"),
        patch("docforge.server.routers.projects.store.list_projects", return_value=[]),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/projects", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_project_not_found(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.projects.store.get_connection"),
        patch("docforge.server.routers.projects.store.get_project", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/projects/nope", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_project_found(tmp_path):
    app = _make_app(tmp_path)
    project = {
        "id": "p1",
        "name": "Test Project",
        "job_id": "j1",
        "input_filename": "f.docx",
        "config_snapshot": "{}",
        "output_paths": "[]",
        "template": "minimal",
        "language": "en",
        "ai_model": "gpt-4o",
        "status": "COMPLETED",
        "created_at": "2024",
        "completed_at": "2024",
    }

    with (
        patch("docforge.server.routers.projects.store.get_connection"),
        patch("docforge.server.routers.projects.store.get_project", return_value=project),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/projects/p1", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["name"] == "Test Project"


@pytest.mark.asyncio
async def test_delete_project_not_found(tmp_path):
    app = _make_app(tmp_path)

    with (
        patch("docforge.server.routers.projects.store.get_connection"),
        patch("docforge.server.routers.projects.store.get_project", return_value=None),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.delete("/projects/nope", headers=AUTH)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_success(tmp_path):
    app = _make_app(tmp_path)
    project = {"id": "p1", "name": "T", "output_paths": "[]"}

    with (
        patch("docforge.server.routers.projects.store.get_connection"),
        patch("docforge.server.routers.projects.store.get_project", return_value=project),
        patch("docforge.server.routers.projects.store.delete_project", return_value=True),
    ):
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            r = await c.delete("/projects/p1", headers=AUTH)
    assert r.status_code == 204
