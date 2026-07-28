"""Integration tests for jobs and projects API routes."""

from __future__ import annotations

import os
import uuid

import httpx
import pytest
from httpx import AsyncClient

from docforge.server import store
from docforge.server.app import create_app
from docforge.server.auth import hash_password

DATABASE_URL = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL not set — skipping PostgreSQL integration tests",
)


@pytest.fixture
def app_dirs(tmp_path):
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "output"
    upload_dir.mkdir()
    output_dir.mkdir()
    return upload_dir, output_dir


@pytest.fixture
def app_with_user(app_dirs):
    upload_dir, output_dir = app_dirs
    store.init_db(DATABASE_URL)
    conn = store.get_connection(DATABASE_URL)
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM projects")
            cur.execute("DELETE FROM jobs")
            cur.execute("DELETE FROM user_accounts")
        store.upsert_user(conn, "admin", hash_password("secret123"))
    finally:
        conn.close()

    app = create_app(
        db_url=DATABASE_URL,
        upload_dir=upload_dir,
        output_dir=output_dir,
        secret_key="test-secret-key-32chars-minimum!!",
        token_ttl_hours=1,
    )
    return app, DATABASE_URL, upload_dir, output_dir


async def _login(client: AsyncClient) -> str:
    resp = await client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    token: str = resp.json()["access_token"]
    return token


# ---------- jobs ----------


@pytest.mark.asyncio
async def test_submit_job_missing_document(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.post(
            "/jobs",
            json={"document_id": "nonexistent-doc-id"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_submit_job_requires_auth(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/jobs", json={"document_id": "x"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_job_requires_auth(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/jobs/some-job-id")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_job_not_found(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.delete(
            "/jobs/nonexistent",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_queued(app_with_user):
    app, db_url, *_ = app_with_user
    job_id = str(uuid.uuid4())
    conn = store.get_connection(db_url)
    try:
        store.insert_job(conn, job_id, "file.docx", "/tmp/file.docx", {})
    finally:
        conn.close()

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.delete(
            f"/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_running_job_rejected(app_with_user):
    app, db_url, *_ = app_with_user
    job_id = str(uuid.uuid4())
    conn = store.get_connection(db_url)
    try:
        store.insert_job(conn, job_id, "file.docx", "/tmp/file.docx", {})
        store.update_job_status(conn, job_id, "RUNNING", "LOADING")
    finally:
        conn.close()

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.delete(
            f"/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_download_job_not_found(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            "/jobs/ghost/download/docx",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_job_unsupported_format(app_with_user):
    app, db_url, *_ = app_with_user
    job_id = str(uuid.uuid4())
    conn = store.get_connection(db_url)
    try:
        store.insert_job(conn, job_id, "f.docx", "/tmp/f.docx", {})
    finally:
        conn.close()

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            f"/jobs/{job_id}/download/pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_download_job_not_completed(app_with_user):
    app, db_url, *_ = app_with_user
    job_id = str(uuid.uuid4())
    conn = store.get_connection(db_url)
    try:
        store.insert_job(conn, job_id, "f.docx", "/tmp/f.docx", {})
    finally:
        conn.close()

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            f"/jobs/{job_id}/download/docx",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 409


# ---------- projects ----------


@pytest.mark.asyncio
async def test_get_project_not_found(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            "/projects/nonexistent",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_project_requires_auth(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/projects/x")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_project_not_found(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.delete(
            "/projects/nonexistent",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_project_crud(app_with_user):
    app, db_url, upload_dir, _output_dir = app_with_user
    job_id = str(uuid.uuid4())
    conn = store.get_connection(db_url)
    try:
        store.insert_job(conn, job_id, "f.docx", str(upload_dir / "f.docx"), {})
        project_id = store.insert_project(
            conn,
            name="Test Project",
            job_id=job_id,
            input_filename="f.docx",
            config={},
            output_paths=[],
            template="minimal",
            language="en",
            ai_model="gpt-4o",
        )
    finally:
        conn.close()

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        # list
        resp = await client.get("/projects", headers=headers)
        assert resp.status_code == 200
        ids = [p["id"] for p in resp.json()]
        assert project_id in ids

        # get
        resp = await client.get(f"/projects/{project_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test Project"

        # delete
        resp = await client.delete(f"/projects/{project_id}", headers=headers)
        assert resp.status_code == 204

        # confirm gone
        resp = await client.get(f"/projects/{project_id}", headers=headers)
        assert resp.status_code == 404
