"""docforge cache — list, clear, stats."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Manage the DocForge cache.")


def _default_cache_dir() -> Path:
    return Path.home() / ".docforge" / "cache"


@app.command("stats")
def stats(
    cache_dir: Path = typer.Option(_default_cache_dir(), "--cache-dir"),
) -> None:
    """Show cache statistics."""
    from docforge.cache.filesystem import FilesystemCache

    table = Table(title="Cache Statistics")
    table.add_column("Bucket")
    table.add_column("Items", justify="right")
    table.add_column("Size (MB)", justify="right")

    total_items = 0
    total_mb = 0.0
    for bucket in ["images", "ai_responses", "default"]:
        try:
            c = FilesystemCache(cache_dir, bucket)
            s = c.stats()
            table.add_row(bucket, str(s["item_count"]), str(s["total_size_mb"]))
            total_items += s["item_count"]
            total_mb += s["total_size_mb"]
        except Exception:
            table.add_row(bucket, "–", "–")

    table.add_section()
    table.add_row("[bold]Total[/bold]", str(total_items), f"{round(total_mb, 2)}")
    console.print(table)


@app.command("clear")
def clear(
    cache_dir: Path = typer.Option(_default_cache_dir(), "--cache-dir"),
    bucket: str = typer.Option(
        "all", "--bucket", help="Bucket to clear: images, ai_responses, or all"
    ),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Clear cached items."""
    from docforge.cache.filesystem import FilesystemCache

    if not confirm:
        typer.confirm(f"Clear {'all buckets' if bucket == 'all' else bucket}?", abort=True)

    buckets = ["images", "ai_responses", "default"] if bucket == "all" else [bucket]
    for b in buckets:
        try:
            FilesystemCache(cache_dir, b).clear()
            console.print(f"[green]✓[/green] Cleared bucket: {b}")
        except Exception as exc:
            console.print(f"[red]Error clearing {b}:[/red] {exc}")


@app.command("list")
def list_items(
    cache_dir: Path = typer.Option(_default_cache_dir(), "--cache-dir"),
    bucket: str = typer.Option("all", "--bucket"),
    limit: int = typer.Option(20, "--limit"),
) -> None:
    """List cached items."""
    buckets = ["images", "ai_responses", "default"] if bucket == "all" else [bucket]
    for b in buckets:
        b_dir = cache_dir / b
        if not b_dir.exists():
            continue
        items = [p for p in b_dir.rglob("*") if p.is_file() and p.suffix != ".json"]
        console.print(f"\n[bold]{b}[/bold] — {len(items)} item(s)")
        for item in items[:limit]:
            size_kb = item.stat().st_size / 1024
            console.print(f"  {item.name[:16]}… {size_kb:.1f} KB")
