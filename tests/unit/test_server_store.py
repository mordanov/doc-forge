"""Unit tests for server/store.py using mock psycopg2 connections."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from docforge.server import store


def _make_conn(fetchone_val=None, fetchall_val=None, rowcount=1):
    """Build a minimal mock psycopg2 connection."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = fetchone_val
    cur.fetchall.return_value = fetchall_val or []
    cur.rowcount = rowcount

    conn = MagicMock()
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cur
    return conn, cur


# --- upsert_user ---


def test_upsert_user_executes_insert():
    conn, cur = _make_conn()
    store.upsert_user(conn, "admin", "hash123")
    cur.execute.assert_called_once()
    sql, params = cur.execute.call_args[0]
    assert "INSERT INTO user_accounts" in sql
    assert "admin" in params
    assert "hash123" in params


# --- get_user ---


def test_get_user_returns_dict():
    row = {"id": 1, "username": "admin", "password_hash": "hashed", "created_at": "2024"}
    conn, cur = _make_conn(fetchone_val=row)
    result = store.get_user(conn)
    assert result == dict(row)


def test_get_user_returns_none_when_missing():
    conn, cur = _make_conn(fetchone_val=None)
    result = store.get_user(conn)
    assert result is None


# --- insert_job ---


def test_insert_job_executes_insert():
    conn, cur = _make_conn()
    store.insert_job(conn, "job-1", "file.docx", "/tmp/file.docx", {"key": "val"})
    cur.execute.assert_called_once()
    sql, params = cur.execute.call_args[0]
    assert "INSERT INTO jobs" in sql
    assert "job-1" in params
    assert "file.docx" in params
    assert json.dumps({"key": "val"}) in params


# --- update_job_status ---


def test_update_job_status_queued():
    conn, cur = _make_conn()
    store.update_job_status(conn, "j1", "QUEUED", "UPLOADING")
    cur.execute.assert_called_once()
    sql = cur.execute.call_args[0][0]
    assert "UPDATE jobs SET" in sql


def test_update_job_status_running_sets_started_at():
    conn, cur = _make_conn()
    store.update_job_status(conn, "j1", "RUNNING", "ANALYSING", progress=5)
    sql = cur.execute.call_args[0][0]
    assert "started_at" in sql


def test_update_job_status_completed_sets_completed_at():
    conn, cur = _make_conn()
    store.update_job_status(conn, "j1", "COMPLETED", "FINISHED", output_paths=["f.docx"])
    sql = cur.execute.call_args[0][0]
    assert "completed_at" in sql
    assert "output_paths" in sql


def test_update_job_status_with_error():
    conn, cur = _make_conn()
    store.update_job_status(conn, "j1", "FAILED", "FINISHED", error="boom")
    sql = cur.execute.call_args[0][0]
    assert "error" in sql


def test_update_job_status_with_warnings():
    conn, cur = _make_conn()
    store.update_job_status(conn, "j1", "COMPLETED", "FINISHED", warnings=["w1"])
    sql = cur.execute.call_args[0][0]
    assert "warnings" in sql


# --- get_job ---


def test_get_job_returns_dict():
    row = {"id": "j1", "status": "QUEUED"}
    conn, cur = _make_conn(fetchone_val=row)
    result = store.get_job(conn, "j1")
    assert result == dict(row)


def test_get_job_returns_none():
    conn, cur = _make_conn(fetchone_val=None)
    result = store.get_job(conn, "missing")
    assert result is None


# --- delete_job ---


def test_delete_job_returns_true_when_deleted():
    conn, cur = _make_conn(rowcount=1)
    assert store.delete_job(conn, "j1") is True


def test_delete_job_returns_false_when_not_found():
    conn, cur = _make_conn(rowcount=0)
    assert store.delete_job(conn, "nope") is False


# --- insert_project ---


def test_insert_project_returns_uuid():
    conn, cur = _make_conn()
    project_id = store.insert_project(
        conn,
        name="My Project",
        job_id="j1",
        input_filename="file.docx",
        config={},
        output_paths=["out.docx"],
        template="minimal",
        language="en",
        ai_model="gpt-4o",
    )
    assert len(project_id) == 36  # UUID
    cur.execute.assert_called_once()


# --- list_projects ---


def test_list_projects_returns_list():
    rows = [{"id": "p1"}, {"id": "p2"}]
    conn, cur = _make_conn(fetchall_val=rows)
    result = store.list_projects(conn)
    assert result == [dict(r) for r in rows]


# --- get_project ---


def test_get_project_returns_dict():
    row = {"id": "p1", "name": "Test"}
    conn, cur = _make_conn(fetchone_val=row)
    result = store.get_project(conn, "p1")
    assert result == dict(row)


def test_get_project_returns_none():
    conn, cur = _make_conn(fetchone_val=None)
    result = store.get_project(conn, "missing")
    assert result is None


# --- delete_project ---


def test_delete_project_returns_true():
    conn, cur = _make_conn(rowcount=1)
    assert store.delete_project(conn, "p1") is True


def test_delete_project_returns_false():
    conn, cur = _make_conn(rowcount=0)
    assert store.delete_project(conn, "p1") is False
