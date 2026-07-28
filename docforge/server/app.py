"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from docforge.logging.setup import get_logger
from docforge.server import store
from docforge.server.routers import auth, documents, jobs, projects, system

logger = get_logger(__name__)


def create_app(
    db_url: str,
    upload_dir: Path,
    output_dir: Path,
    secret_key: str,
    token_ttl_hours: int = 24,
) -> FastAPI:
    app = FastAPI(title="DocForge API", version="1.0.0")

    app.state.db_url = db_url
    app.state.upload_dir = str(upload_dir)
    app.state.output_dir = str(output_dir)
    app.state.secret_key = secret_key
    app.state.token_ttl_hours = token_ttl_hours

    @app.on_event("startup")
    async def startup():
        import os

        from docforge.server.auth import hash_password

        store.init_db(db_url)
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        conn = store.get_connection(db_url)
        user = store.get_user(conn)
        conn.close()
        if not user:
            username = os.getenv("DOCFORGE_USERNAME", "").strip()
            password = os.getenv("DOCFORGE_PASSWORD", "").strip()
            if username and len(password) >= 8:
                conn2 = store.get_connection(db_url)
                store.upsert_user(conn2, username, hash_password(password))
                conn2.close()
                logger.info("user_auto_provisioned", username=username)
            else:
                logger.warning("docforge_not_initialised", hint="Run `docforge init` first")

        from docforge.server.jobs import get_job_queue

        queue = get_job_queue(db_url)
        queue.start()
        logger.info("server_started", db=db_url.split("@")[-1] if "@" in db_url else db_url)

    @app.on_event("shutdown")
    async def shutdown():
        from docforge.server.jobs import get_job_queue

        queue = get_job_queue(db_url)
        queue.stop()

    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(jobs.router)
    app.include_router(projects.router)
    app.include_router(system.router)

    return app
