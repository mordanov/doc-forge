"""docforge init — provision the single user account."""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

from docforge.logging.setup import setup_logging
from docforge.server import store
from docforge.server.auth import hash_password

console = Console()


def init_command(
    force: bool = typer.Option(False, "--force", help="Overwrite existing user account"),
    db: Path = typer.Option(
        Path.home() / ".docforge" / "docforge.db",
        "--db",
        help="Path to SQLite database",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Provision the single-user account from .env credentials."""
    setup_logging(level="DEBUG" if verbose else "INFO")

    from dotenv import load_dotenv

    load_dotenv()

    username = os.getenv("DOCFORGE_USERNAME", "").strip()
    password = os.getenv("DOCFORGE_PASSWORD", "").strip()
    secret_key = os.getenv("DOCFORGE_SECRET_KEY", "").strip()

    errors = []
    if not username:
        errors.append("DOCFORGE_USERNAME is not set in .env")
    if len(password) < 8:
        errors.append("DOCFORGE_PASSWORD must be at least 8 characters")
    if len(secret_key) < 32:
        errors.append("DOCFORGE_SECRET_KEY must be at least 32 characters")

    if errors:
        for err in errors:
            console.print(f"[red]Error:[/red] {err}")
        raise typer.Exit(1)

    store.init_db(db)
    conn = store.get_connection(db)
    existing = store.get_user(conn)

    if existing and not force:
        console.print(
            f"[yellow]User '{existing['username']}' already exists. Use --force to overwrite.[/yellow]"
        )
        raise typer.Exit(1)

    password_hash = hash_password(password)
    store.upsert_user(conn, username, password_hash)
    conn.commit()

    console.print(f"[green]✓[/green] User '{username}' created successfully.")
    console.print(f"  Database: {db}")
    console.print("  Run [cyan]docforge server start[/cyan] to start the API server.")
