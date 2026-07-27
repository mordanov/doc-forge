"""docforge analyse — analyse a .docx and report structure without modifying it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from docforge.document.analyser import analyse
from docforge.logging.setup import setup_logging

console = Console()


def _file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyse_command(
    input_file: Path = typer.Argument(..., help="Source .docx file to analyse"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text or json"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Analyse document structure. Source file is never modified."""
    setup_logging(level="DEBUG" if verbose else "INFO")

    if not input_file.exists():
        console.print(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)

    checksum_before = _file_checksum(input_file)
    model, issues = analyse(input_file)
    checksum_after = _file_checksum(input_file)

    if checksum_before != checksum_after:
        console.print("[red]Error:[/red] Source file was modified during analysis!")
        raise typer.Exit(2)

    stats = model.statistics

    if format == "json":
        report = {
            "file": str(input_file),
            "statistics": {
                "chapters": stats.chapter_count,
                "headings": stats.heading_count,
                "tables": stats.table_count,
                "image_placeholders": stats.placeholder_count,
                "words": stats.word_count,
                "estimated_pages": stats.page_count_estimate,
            },
            "chapters": [
                {
                    "id": ch.id,
                    "title": ch.title,
                    "elements": len(ch.elements),
                }
                for ch in model.chapters
            ],
            "issues": [
                {"code": i.code, "message": i.message, "location": i.location} for i in issues
            ],
        }
        console.print(json.dumps(report, indent=2))
        return

    console.print(f"\n[bold]Document Analysis:[/bold] {input_file.name}\n")

    table = Table(title="Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("Chapters", str(stats.chapter_count))
    table.add_row("Headings", str(stats.heading_count))
    table.add_row("Tables", str(stats.table_count))
    table.add_row("Image Placeholders", str(stats.placeholder_count))
    table.add_row("Word Count", str(stats.word_count))
    table.add_row("Est. Pages", str(stats.page_count_estimate))
    console.print(table)

    if model.chapters:
        console.print("\n[bold]Chapters:[/bold]")
        for ch in model.chapters:
            console.print(f"  • {ch.title} ({len(ch.elements)} elements)")

    if issues:
        console.print(f"\n[yellow]Issues ({len(issues)}):[/yellow]")
        for issue in issues:
            loc = f" @ {issue.location}" if issue.location else ""
            console.print(f"  [{issue.code}] {issue.message}{loc}")
    else:
        console.print("\n[green]No issues detected.[/green]")
