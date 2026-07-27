"""docforge prompts — list loaded prompt templates."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()


def prompts_command() -> None:
    """List available prompt templates."""
    from docforge.ai.prompts.loader import list_prompts

    prompts = list_prompts()

    if not prompts:
        console.print("[yellow]No prompts found.[/yellow]")
        return

    table = Table(title="Available Prompts")
    table.add_column("ID", style="cyan")
    table.add_column("Version")
    table.add_column("Providers")
    table.add_column("Description")

    for p in prompts:
        table.add_row(
            p.id,
            p.version,
            ", ".join(p.providers),
            p.description[:60],
        )

    console.print(table)
