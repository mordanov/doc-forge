"""Integration tests for PostgreSQL store — real database, no mocks."""

import os

import pytest

from docforge.server import store

DATABASE_URL = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL not set — skipping PostgreSQL integration tests",
)


@pytest.fixture
def db():
    store.init_db(DATABASE_URL)
    conn = store.get_connection(DATABASE_URL)
    # Wipe tables before each test for isolation
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM projects")
        cur.execute("DELETE FROM jobs")
        cur.execute("DELETE FROM user_accounts")
    yield DATABASE_URL
    conn.close()


def test_init_db_creates_tables(db):
    conn = store.get_connection(db)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = {row[0] for row in cur.fetchall()}
    finally:
        conn.close()
    assert "user_accounts" in tables
    assert "jobs" in tables
    assert "projects" in tables


def test_init_db_idempotent(db):
    store.init_db(db)


def test_upsert_and_get_user(db):
    conn = store.get_connection(db)
    try:
        assert store.get_user(conn) is None

        store.upsert_user(conn, "admin", "$2b$12$fakehash")
        user = store.get_user(conn)
        assert user is not None
        assert user["username"] == "admin"
        assert user["password_hash"] == "$2b$12$fakehash"
    finally:
        conn.close()


def test_upsert_user_overwrites(db):
    conn = store.get_connection(db)
    try:
        store.upsert_user(conn, "admin", "hash1")
        store.upsert_user(conn, "admin2", "hash2")
        user = store.get_user(conn)
        assert user is not None
        assert user["username"] == "admin2"
        assert user["password_hash"] == "hash2"
    finally:
        conn.close()


def test_job_lifecycle(db):
    conn = store.get_connection(db)
    try:
        store.insert_job(conn, "job-1", "input.docx", "/tmp/input.docx", {"template": "minimal"})
        job = store.get_job(conn, "job-1")
        assert job is not None
        assert job["status"] == "QUEUED"
        assert job["stage"] == "UPLOADING"

        store.update_job_status(conn, "job-1", "RUNNING", "ANALYSING", progress=15, elapsed=1.5)
        job = store.get_job(conn, "job-1")
        assert job is not None
        assert job["status"] == "RUNNING"
        assert job["progress"] == 15

        store.update_job_status(
            conn, "job-1", "COMPLETED", "FINISHED", progress=100, output_paths=["/tmp/output.docx"]
        )
        job = store.get_job(conn, "job-1")
        assert job is not None
        assert job["status"] == "COMPLETED"
        assert job["completed_at"] is not None
    finally:
        conn.close()


def test_project_crud(db):
    conn = store.get_connection(db)
    try:
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
        assert project is not None
        assert project["name"] == "Test Project"
        assert project["template"] == "minimal"

        projects = store.list_projects(conn)
        assert len(projects) == 1

        store.delete_project(conn, pid)
        assert store.get_project(conn, pid) is None
    finally:
        conn.close()


def test_delete_nonexistent_job(db):
    conn = store.get_connection(db)
    try:
        result = store.delete_job(conn, "nonexistent")
        assert result is False
    finally:
        conn.close()
