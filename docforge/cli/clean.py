"""docforge clean — remove temporary files and old outputs."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def clean_command(
    output_dir: Path = typer.Option(
        Path.home() / ".docforge" / "outputs",
        "--output-dir",
        help="Directory with job outputs",
    ),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Remove temporary files and old job outputs."""
    if not output_dir.exists():
        console.print(f"[yellow]Output directory does not exist:[/yellow] {output_dir}")
        return

    files = list(output_dir.glob("*.docx"))
    if not files:
        console.print("[green]Nothing to clean.[/green]")
        return

    console.print(f"Found {len(files)} output file(s) in {output_dir}")
    if not confirm:
        typer.confirm("Delete all output files?", abort=True)

    deleted = 0
    for f in files:
        try:
            f.unlink()
            deleted += 1
        except Exception as exc:
            console.print(f"[red]Error deleting {f.name}:[/red] {exc}")

    console.print(f"[green]✓[/green] Deleted {deleted} file(s).")
