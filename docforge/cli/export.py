"""docforge export — export to additional formats (v1: docx only)."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def export_command(
    input_file: Path = typer.Argument(..., help="Rendered .docx to export"),
    output_file: Path = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("docx", "--format", "-f", help="Output format"),
) -> None:
    """Export a rendered document to a target format."""
    if format != "docx":
        console.print(
            f"[yellow]Format '{format}' is not available in v1.0. Only 'docx' is supported.[/yellow]"
        )
        raise typer.Exit(1)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)

    import shutil

    output_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(input_file), str(output_file))
    console.print(f"[green]✓[/green] Exported: {output_file}")
