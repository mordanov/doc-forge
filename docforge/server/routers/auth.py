"""Auth router — POST /auth/login."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from docforge.server import store
from docforge.server.auth import LoginRequest, TokenResponse, create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request) -> TokenResponse:
    conn = store.get_connection(request.app.state.db_url)
    try:
        user = store.get_user(conn)
    finally:
        conn.close()

    if not user:
        raise HTTPException(status_code=503, detail="Server not initialised — run `docforge init`")

    if body.username != user["username"] or not verify_password(
        body.password, user["password_hash"]
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(
        user["username"],
        request.app.state.secret_key,
        ttl_hours=request.app.state.token_ttl_hours,
    )
    return TokenResponse(access_token=token)
