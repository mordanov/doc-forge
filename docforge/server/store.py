"""PostgreSQL database setup and CRUD operations."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import psycopg2
import psycopg2.extras

_DDL = """
CREATE TABLE IF NOT EXISTS user_accounts (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id              TEXT PRIMARY KEY,
    project_id      TEXT,
    status          TEXT NOT NULL,
    stage           TEXT NOT NULL,
    progress        INTEGER NOT NULL DEFAULT 0,
    elapsed_seconds REAL NOT NULL DEFAULT 0,
    config_snapshot TEXT NOT NULL,
    input_filename  TEXT NOT NULL,
    input_path      TEXT NOT NULL,
    output_paths    TEXT NOT NULL DEFAULT '[]',
    warnings        TEXT NOT NULL DEFAULT '[]',
    error           TEXT,
    created_at      TEXT NOT NULL,
    started_at      TEXT,
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    job_id          TEXT NOT NULL,
    input_filename  TEXT NOT NULL,
    config_snapshot TEXT NOT NULL,
    output_paths    TEXT NOT NULL,
    template        TEXT NOT NULL,
    language        TEXT NOT NULL,
    ai_model        TEXT NOT NULL,
    status          TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    completed_at    TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
"""


def init_db(db_url: str) -> None:
    conn = psycopg2.connect(db_url)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(_DDL)
    finally:
        conn.close()


def get_connection(db_url: str) -> psycopg2.extensions.connection:
    conn = psycopg2.connect(db_url)
    psycopg2.extras.register_default_jsonb(conn)
    return conn


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# UserAccount CRUD
# ---------------------------------------------------------------------------


def upsert_user(conn: psycopg2.extensions.connection, username: str, password_hash: str) -> None:
    with conn, conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO user_accounts (id, username, password_hash, created_at)
                VALUES (1, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                  SET username = EXCLUDED.username,
                      password_hash = EXCLUDED.password_hash,
                      created_at = EXCLUDED.created_at
                """,
            (username, password_hash, _now()),
        )


def get_user(conn: psycopg2.extensions.connection) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM user_accounts WHERE id = 1")
        row = cur.fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Job CRUD
# ---------------------------------------------------------------------------


def insert_job(
    conn: psycopg2.extensions.connection,
    job_id: str,
    input_filename: str,
    input_path: str,
    config: dict,
) -> None:
    with conn, conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO jobs
                  (id, status, stage, progress, elapsed_seconds, config_snapshot,
                   input_filename, input_path, output_paths, warnings, created_at)
                VALUES (%s, 'QUEUED', 'UPLOADING', 0, 0, %s, %s, %s, '[]', '[]', %s)
                """,
            (job_id, json.dumps(config), input_filename, input_path, _now()),
        )


def update_job_status(
    conn: psycopg2.extensions.connection,
    job_id: str,
    status: str,
    stage: str,
    progress: int = 0,
    elapsed: float = 0.0,
    error: str | None = None,
    output_paths: list[str] | None = None,
    warnings: list[str] | None = None,
) -> None:
    parts: list[str] = ["status = %s", "stage = %s", "progress = %s", "elapsed_seconds = %s"]
    params: list[Any] = [status, stage, progress, elapsed]

    if status == "RUNNING" and not error:
        parts.append("started_at = COALESCE(started_at, %s)")
        params.append(_now())
    if status in ("COMPLETED", "FAILED", "CANCELLED"):
        parts.append("completed_at = %s")
        params.append(_now())
    if error is not None:
        parts.append("error = %s")
        params.append(error)
    if output_paths is not None:
        parts.append("output_paths = %s")
        params.append(json.dumps(output_paths))
    if warnings is not None:
        parts.append("warnings = %s")
        params.append(json.dumps(warnings))

    params.append(job_id)
    with conn, conn.cursor() as cur:
        cur.execute(f"UPDATE jobs SET {', '.join(parts)} WHERE id = %s", params)  # nosec B608


def get_job(conn: psycopg2.extensions.connection, job_id: str) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()
    return dict(row) if row else None


def delete_job(conn: psycopg2.extensions.connection, job_id: str) -> bool:
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
        rowcount: int = cur.rowcount
        return rowcount > 0


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------


def insert_project(
    conn: psycopg2.extensions.connection,
    name: str,
    job_id: str,
    input_filename: str,
    config: dict,
    output_paths: list[str],
    template: str,
    language: str,
    ai_model: str,
    status: str = "COMPLETED",
) -> str:
    project_id = str(uuid.uuid4())
    with conn, conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO projects
                  (id, name, job_id, input_filename, config_snapshot,
                   output_paths, template, language, ai_model, status, created_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
            (
                project_id,
                name,
                job_id,
                input_filename,
                json.dumps(config),
                json.dumps(output_paths),
                template,
                language,
                ai_model,
                status,
                _now(),
                _now(),
            ),
        )
    return project_id


def list_projects(
    conn: psycopg2.extensions.connection, offset: int = 0, limit: int = 20
) -> list[dict]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM projects ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]


def get_project(conn: psycopg2.extensions.connection, project_id: str) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        row = cur.fetchone()
    return dict(row) if row else None


def delete_project(conn: psycopg2.extensions.connection, project_id: str) -> bool:
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        rowcount: int = cur.rowcount
        return rowcount > 0
