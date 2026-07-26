"""docforge render — render a .docx to publication-quality DOCX."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docforge.core.pipeline import render_pipeline
from docforge.core.rendering import RenderStage
from docforge.logging.setup import setup_logging

app = typer.Typer(help="Render a Word document to publication quality.")
console = Console()


@app.command()
def render(
    input_file: Path = typer.Argument(..., help="Source .docx file"),
    output_file: Path = typer.Argument(..., help="Output .docx path"),
    template: str = typer.Option("minimal", "--template", "-t", help="Theme to apply"),
    language: str = typer.Option("en", "--language", "-l", help="Document language (ISO 639-1)"),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="AI model"),
    creativity: int = typer.Option(
        5, "--creativity", "-c", min=1, max=10, help="AI creativity (1-10)"
    ),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI, use default layout decisions"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    config: Path | None = typer.Option(None, "--config", help="Config file path"),
    profile: str | None = typer.Option(None, "--profile", help="Config profile"),
) -> None:
    setup_logging(level="DEBUG" if verbose else "INFO")

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_file}")
        raise typer.Exit(1)

    if input_file.suffix.lower() != ".docx":
        console.print("[red]Error:[/red] Input must be a .docx file")
        raise typer.Exit(1)

    stages_seen: list[str] = []

    def on_stage(stage: RenderStage, progress: int, message: str) -> None:
        stages_seen.append(message)
        if verbose:
            console.print(f"  [{progress:3d}%] {message}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Rendering...", total=None)

        async def _run():
            return await render_pipeline(
                input_path=input_file,
                output_path=output_file,
                template=template,
                language=language,
                ai_provider=None,  # AI provider injected via config in future
                ai_model=model,
                creativity=creativity,
                on_stage=on_stage,
            )

        report = asyncio.run(_run())
        progress.update(task, description="Complete")

    if report.succeeded():
        console.print(f"[green]✓[/green] Rendered: {output_file}")
        if report.warnings:
            console.print(f"  [yellow]{len(report.warnings)} warning(s)[/yellow]")
            if verbose:
                for w in report.warnings:
                    console.print(f"  [yellow]•[/yellow] {w}")
        if report.recovered_errors:
            console.print(f"  [yellow]{len(report.recovered_errors)} recovered error(s)[/yellow]")
        console.print(f"  Duration: {report.duration_seconds:.1f}s")
    else:
        console.print(f"[red]✗ Rendering failed:[/red] {report.fatal_failure}")
        raise typer.Exit(1)
