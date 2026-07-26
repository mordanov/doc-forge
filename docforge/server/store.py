"""SQLite database setup and CRUD operations."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_DDL = """
CREATE TABLE IF NOT EXISTS user_accounts (
    id            INTEGER PRIMARY KEY,
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


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_DDL)
        conn.commit()


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# UserAccount CRUD
# ---------------------------------------------------------------------------


def upsert_user(conn: sqlite3.Connection, username: str, password_hash: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO user_accounts (id, username, password_hash, created_at) "
        "VALUES (1, ?, ?, ?)",
        (username, password_hash, _now()),
    )
    conn.commit()


def get_user(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute("SELECT * FROM user_accounts WHERE id = 1").fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Job CRUD
# ---------------------------------------------------------------------------


def insert_job(
    conn: sqlite3.Connection, job_id: str, input_filename: str, input_path: str, config: dict
) -> None:
    conn.execute(
        "INSERT INTO jobs (id, status, stage, progress, elapsed_seconds, config_snapshot, "
        "input_filename, input_path, output_paths, warnings, created_at) "
        "VALUES (?, 'QUEUED', 'UPLOADING', 0, 0, ?, ?, ?, '[]', '[]', ?)",
        (job_id, json.dumps(config), input_filename, input_path, _now()),
    )
    conn.commit()


def update_job_status(
    conn: sqlite3.Connection,
    job_id: str,
    status: str,
    stage: str,
    progress: int = 0,
    elapsed: float = 0.0,
    error: str | None = None,
    output_paths: list[str] | None = None,
    warnings: list[str] | None = None,
) -> None:
    fields = "status = ?, stage = ?, progress = ?, elapsed_seconds = ?"
    params: list[Any] = [status, stage, progress, elapsed]

    if status == "RUNNING" and not error:
        fields += ", started_at = COALESCE(started_at, ?)"
        params.append(_now())
    if status in ("COMPLETED", "FAILED", "CANCELLED"):
        fields += ", completed_at = ?"
        params.append(_now())
    if error is not None:
        fields += ", error = ?"
        params.append(error)
    if output_paths is not None:
        fields += ", output_paths = ?"
        params.append(json.dumps(output_paths))
    if warnings is not None:
        fields += ", warnings = ?"
        params.append(json.dumps(warnings))

    params.append(job_id)
    conn.execute(f"UPDATE jobs SET {fields} WHERE id = ?", params)  # nosec B608
    conn.commit()


def get_job(conn: sqlite3.Connection, job_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def delete_job(conn: sqlite3.Connection, job_id: str) -> bool:
    cur = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------


def insert_project(
    conn: sqlite3.Connection,
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
    conn.execute(
        "INSERT INTO projects (id, name, job_id, input_filename, config_snapshot, "
        "output_paths, template, language, ai_model, status, created_at, completed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
    conn.commit()
    return project_id


def list_projects(conn: sqlite3.Connection, offset: int = 0, limit: int = 20) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [dict(r) for r in rows]


def get_project(conn: sqlite3.Connection, project_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None


def delete_project(conn: sqlite3.Connection, project_id: str) -> bool:
    cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    return cur.rowcount > 0
