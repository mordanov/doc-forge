"""docforge themes — list available themes."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from docforge.templates.engine import list_themes

console = Console()


def themes_command() -> None:
    """List all available themes."""
    themes = list_themes()
    if not themes:
        console.print("[yellow]No themes found.[/yellow]")
        return

    table = Table(title="Available Themes")
    table.add_column("ID", style="cyan")
    table.add_column("Version")
    table.add_column("Author")
    table.add_column("Cover", justify="center")
    table.add_column("Sidebars", justify="center")

    for theme in themes:
        manifest = theme.get("manifest", {})
        table.add_row(
            theme.get("id", ""),
            theme.get("version", ""),
            theme.get("author", ""),
            "✓" if manifest.get("supports_cover") else "–",
            "✓" if manifest.get("supports_sidebars") else "–",
        )

    console.print(table)
