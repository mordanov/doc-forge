"""docforge validate — validate config, templates, and optionally a document."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from docforge.logging.setup import setup_logging

console = Console()


def validate_command(
    config: Path | None = typer.Option(None, "--config", help="Config file to validate"),
    document: Path | None = typer.Option(None, "--document", help="Document to validate"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Validate configuration and/or document structure."""
    setup_logging(level="DEBUG" if verbose else "INFO")
    errors: list[str] = []
    warnings: list[str] = []

    if config is not None:
        if not config.exists():
            errors.append(f"Config file not found: {config}")
        else:
            try:
                from docforge.config.loader import load_config

                load_config(config_file=config)
                console.print(f"[green]✓[/green] Config valid: {config}")
            except Exception as exc:
                errors.append(f"Config validation failed: {exc}")

    if document is not None:
        if not document.exists():
            errors.append(f"Document not found: {document}")
        elif document.suffix.lower() != ".docx":
            errors.append(f"Expected .docx, got: {document.suffix}")
        else:
            try:
                from docforge.document.analyser import analyse
                from docforge.rendering.layout_validator import validate as validate_layout

                model, issues = analyse(document)
                summary = validate_layout(model)
                console.print(f"[green]✓[/green] Document analysed: {document}")
                for w in summary.warnings:
                    warnings.append(f"[{w.code}] {w.message}")
                for e in summary.errors:
                    errors.append(f"[{e.code}] {e.message}")
                for issue in issues:
                    warnings.append(f"[{issue.code}] {issue.message}")
            except Exception as exc:
                errors.append(f"Document validation failed: {exc}")

    if not config and not document:
        console.print("[yellow]Nothing to validate. Use --config and/or --document.[/yellow]")
        return

    if warnings:
        console.print(f"\n[yellow]{len(warnings)} warning(s):[/yellow]")
        for warn_msg in warnings:
            console.print(f"  [yellow]•[/yellow] {warn_msg}")

    if errors:
        console.print(f"\n[red]{len(errors)} error(s):[/red]")
        for err_msg in errors:
            console.print(f"  [red]✗[/red] {err_msg}")
        raise typer.Exit(1)
    else:
        console.print("\n[green]Validation passed.[/green]")
