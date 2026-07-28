"""docforge server — start/stop/status the HTTP API server."""

from __future__ import annotations

import os
import signal
from pathlib import Path

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Manage the DocForge HTTP API server.")

_PID_FILE = Path.home() / ".docforge" / "server.pid"


@app.command("start")
def start(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host"),
    port: int = typer.Option(8000, "--port", help="Bind port"),
    upload_dir: Path = typer.Option(Path.home() / ".docforge" / "uploads", "--upload-dir"),
    output_dir: Path = typer.Option(Path.home() / ".docforge" / "outputs", "--output-dir"),
    workers: int = typer.Option(1, "--workers", help="Number of Uvicorn workers"),
) -> None:
    """Start the DocForge API server."""
    from dotenv import load_dotenv

    load_dotenv()

    secret_key = os.getenv("DOCFORGE_SECRET_KEY", "")
    if len(secret_key) < 32:
        console.print("[red]Error:[/red] DOCFORGE_SECRET_KEY must be at least 32 characters")
        raise typer.Exit(1)

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        console.print("[red]Error:[/red] DATABASE_URL environment variable is required")
        raise typer.Exit(1)

    token_ttl = int(os.getenv("DOCFORGE_TOKEN_TTL_HOURS", "24"))

    import uvicorn

    from docforge.server.app import create_app

    application = create_app(
        db_url=db_url,
        upload_dir=upload_dir,
        output_dir=output_dir,
        secret_key=secret_key,
        token_ttl_hours=token_ttl,
    )

    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PID_FILE.write_text(str(os.getpid()))

    console.print(f"[green]Starting DocForge server[/green] on {host}:{port}")
    try:
        uvicorn.run(application, host=host, port=port, workers=workers)
    finally:
        _PID_FILE.unlink(missing_ok=True)


@app.command("stop")
def stop() -> None:
    """Stop a running DocForge server."""
    if not _PID_FILE.exists():
        console.print("[yellow]Server is not running (no PID file found).[/yellow]")
        return
    pid = int(_PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        _PID_FILE.unlink(missing_ok=True)
        console.print(f"[green]✓[/green] Sent SIGTERM to PID {pid}")
    except ProcessLookupError:
        console.print(f"[yellow]Process {pid} not found. Cleaning up PID file.[/yellow]")
        _PID_FILE.unlink(missing_ok=True)


@app.command("status")
def status_cmd() -> None:
    """Check if the DocForge server is running."""
    if not _PID_FILE.exists():
        console.print("[yellow]Server is not running.[/yellow]")
        return
    pid = int(_PID_FILE.read_text().strip())
    try:
        os.kill(pid, 0)
        console.print(f"[green]Server is running[/green] (PID {pid})")
    except ProcessLookupError:
        console.print(f"[yellow]Stale PID file (PID {pid} not running).[/yellow]")
        _PID_FILE.unlink(missing_ok=True)
