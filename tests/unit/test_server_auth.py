"""Unit tests for server/auth.py — no DB required."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from docforge.server.auth import (
    ALGORITHM,
    create_token,
    decode_token,
    hash_password,
    make_auth_dependency,
    verify_password,
)

SECRET = "test-secret-key-minimum-32-chars!!"


def test_hash_produces_non_plaintext():
    h = hash_password("mypassword")
    assert h != "mypassword"
    assert h.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("correct")
    assert verify_password("correct", h) is True


def test_verify_password_wrong():
    h = hash_password("correct")
    assert verify_password("wrong", h) is False


def test_create_and_decode_token_roundtrip():
    token = create_token("alice", SECRET, ttl_hours=1)
    username = decode_token(token, SECRET)
    assert username == "alice"


def test_decode_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc:
        decode_token("not.a.valid.token", SECRET)
    assert exc.value.status_code == 401
    assert "Invalid or expired" in exc.value.detail


def test_decode_token_wrong_secret_raises_401():
    token = create_token("alice", SECRET)
    with pytest.raises(HTTPException) as exc:
        decode_token(token, "wrong-secret-minimum-32-charszz")
    assert exc.value.status_code == 401


def test_decode_token_empty_sub_raises_401():
    payload = {"sub": "", "exp": datetime.now(UTC) + timedelta(hours=1)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        decode_token(token, SECRET)
    assert exc.value.status_code == 401
    assert "Invalid token" in exc.value.detail


def test_decode_expired_token_raises_401():
    payload = {"sub": "alice", "exp": datetime.now(UTC) - timedelta(seconds=1)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        decode_token(token, SECRET)
    assert exc.value.status_code == 401


def test_make_auth_dependency_returns_callable():
    dep = make_auth_dependency(SECRET)
    assert callable(dep)
