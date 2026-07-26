"""Integration tests for SQLite store — real database, no mocks."""

import tempfile
from pathlib import Path

import pytest

from docforge.server import store


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        store.init_db(db_path)
        yield db_path


def test_init_db_creates_tables(db):
    conn = store.get_connection(db)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert "user_accounts" in tables
    assert "jobs" in tables
    assert "projects" in tables


def test_init_db_idempotent(db):
    # Calling init_db again should not raise
    store.init_db(db)


def test_upsert_and_get_user(db):
    conn = store.get_connection(db)
    assert store.get_user(conn) is None

    store.upsert_user(conn, "admin", "$2b$12$fakehash")
    user = store.get_user(conn)
    assert user is not None
    assert user["username"] == "admin"
    assert user["password_hash"] == "$2b$12$fakehash"


def test_upsert_user_overwrites(db):
    conn = store.get_connection(db)
    store.upsert_user(conn, "admin", "hash1")
    store.upsert_user(conn, "admin2", "hash2")
    user = store.get_user(conn)
    assert user["username"] == "admin2"
    assert user["password_hash"] == "hash2"


def test_job_lifecycle(db):
    conn = store.get_connection(db)

    store.insert_job(conn, "job-1", "input.docx", "/tmp/input.docx", {"template": "minimal"})
    job = store.get_job(conn, "job-1")
    assert job is not None
    assert job["status"] == "QUEUED"
    assert job["stage"] == "UPLOADING"

    store.update_job_status(conn, "job-1", "RUNNING", "ANALYSING", progress=15, elapsed=1.5)
    job = store.get_job(conn, "job-1")
    assert job["status"] == "RUNNING"
    assert job["progress"] == 15

    store.update_job_status(
        conn, "job-1", "COMPLETED", "FINISHED", progress=100, output_paths=["/tmp/output.docx"]
    )
    job = store.get_job(conn, "job-1")
    assert job["status"] == "COMPLETED"
    assert job["completed_at"] is not None


def test_project_crud(db):
    conn = store.get_connection(db)

    store.insert_job(conn, "job-1", "input.docx", "/tmp/input.docx", {})
    pid = store.insert_project(
        conn,
        "Test Project",
        "job-1",
        "input.docx",
        {},
        ["/tmp/out.docx"],
        "minimal",
        "en",
        "gpt-4o",
    )
    assert pid is not None

    project = store.get_project(conn, pid)
    assert project["name"] == "Test Project"
    assert project["template"] == "minimal"

    projects = store.list_projects(conn)
    assert len(projects) == 1

    store.delete_project(conn, pid)
    assert store.get_project(conn, pid) is None


def test_delete_nonexistent_job(db):
    conn = store.get_connection(db)
    result = store.delete_job(conn, "nonexistent")
    assert result is False
