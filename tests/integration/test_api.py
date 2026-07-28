"""HTTP API integration tests using httpx.AsyncClient."""

import os
from pathlib import Path

import httpx
import pytest
from httpx import AsyncClient

from docforge.server import store
from docforge.server.app import create_app
from docforge.server.auth import hash_password

SAMPLE_GUIDE = Path(__file__).parents[2] / "examples" / "sample-guide.docx"
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


@pytest.mark.asyncio
async def test_health_endpoint(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/system/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_themes_endpoint(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/system/themes")
    assert resp.status_code == 200
    themes = resp.json()
    assert isinstance(themes, list)
    ids = [t["id"] for t in themes]
    assert "minimal" in ids


@pytest.mark.asyncio
async def test_providers_endpoint(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/system/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert "ai" in data
    assert "images" in data


@pytest.mark.asyncio
async def test_login_valid_credentials(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})
    assert resp.status_code == 401


async def _login(client: AsyncClient) -> str:
    resp = await client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    token: str = resp.json()["access_token"]
    return token


@pytest.mark.asyncio
@pytest.mark.skipif(not SAMPLE_GUIDE.exists(), reason="Sample fixture not found")
async def test_document_upload(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        with open(SAMPLE_GUIDE, "rb") as f:
            resp = await client.post(
                "/documents/upload",
                files={
                    "file": (
                        "sample-guide.docx",
                        f,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
                headers=headers,
            )

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["filename"] == "sample-guide.docx"


@pytest.mark.asyncio
async def test_upload_requires_auth(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/documents/upload",
            files={"file": ("test.docx", b"fake", "application/octet-stream")},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_rejects_non_docx(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.post(
            "/documents/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
@pytest.mark.skipif(not SAMPLE_GUIDE.exists(), reason="Sample fixture not found")
async def test_analyse_document(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        with open(SAMPLE_GUIDE, "rb") as f:
            upload_resp = await client.post(
                "/documents/upload",
                files={
                    "file": (
                        "sample-guide.docx",
                        f,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
                headers=headers,
            )
        doc_id = upload_resp.json()["id"]

        resp = await client.post(f"/documents/{doc_id}/analyse", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "statistics" in data
    assert "chapters" in data["statistics"]


@pytest.mark.asyncio
async def test_get_nonexistent_job(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            "/jobs/nonexistent-job-id",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_project_list_empty(app_with_user):
    app, *_ = app_with_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = await _login(client)
        resp = await client.get(
            "/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    assert resp.json() == []
