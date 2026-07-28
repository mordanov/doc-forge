"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from docforge.logging.setup import get_logger
from docforge.server import store
from docforge.server.routers import auth, documents, jobs, projects, system

logger = get_logger(__name__)


def create_app(
    db_path: Path,
    upload_dir: Path,
    output_dir: Path,
    secret_key: str,
    token_ttl_hours: int = 24,
) -> FastAPI:
    app = FastAPI(title="DocForge API", version="1.0.0")

    app.state.db_path = str(db_path)
    app.state.upload_dir = str(upload_dir)
    app.state.output_dir = str(output_dir)
    app.state.secret_key = secret_key
    app.state.token_ttl_hours = token_ttl_hours

    @app.on_event("startup")
    async def startup():
        import os

        from docforge.server.auth import hash_password

        store.init_db(db_path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        conn = store.get_connection(db_path)
        user = store.get_user(conn)
        if not user:
            username = os.getenv("DOCFORGE_USERNAME", "").strip()
            password = os.getenv("DOCFORGE_PASSWORD", "").strip()
            if username and len(password) >= 8:
                store.upsert_user(conn, username, hash_password(password))
                logger.info("user_auto_provisioned", username=username)
            else:
                logger.warning("docforge_not_initialised", hint="Run `docforge init` first")

        from docforge.server.jobs import get_job_queue

        queue = get_job_queue(db_path)
        queue.start()
        logger.info("server_started", db=str(db_path))

    @app.on_event("shutdown")
    async def shutdown():
        from docforge.server.jobs import get_job_queue

        queue = get_job_queue(db_path)
        queue.stop()

    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(jobs.router)
    app.include_router(projects.router)
    app.include_router(system.router)

    return app
