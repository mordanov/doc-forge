"""docforge providers — list AI and image provider availability."""

from __future__ import annotations

import os

from rich.console import Console
from rich.table import Table

console = Console()


def providers_command() -> None:
    """List all registered providers with availability status."""
    from dotenv import load_dotenv

    load_dotenv()

    table = Table(title="Providers")
    table.add_column("Type")
    table.add_column("ID", style="cyan")
    table.add_column("Status")
    table.add_column("Note")

    # AI providers
    try:
        import openai  # noqa: F401

        key = os.getenv("OPENAI_API_KEY", "")
        if key:
            table.add_row("AI", "openai", "[green]available[/green]", "API key set")
        else:
            table.add_row("AI", "openai", "[yellow]no key[/yellow]", "Set OPENAI_API_KEY")
    except ImportError:
        table.add_row("AI", "openai", "[red]unavailable[/red]", "openai package not installed")

    # Image providers
    table.add_row("Image", "wikimedia", "[green]available[/green]", "No API key required")

    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    if unsplash_key:
        table.add_row("Image", "unsplash", "[green]available[/green]", "API key set")
    else:
        table.add_row("Image", "unsplash", "[yellow]no key[/yellow]", "Set UNSPLASH_ACCESS_KEY")

    pexels_key = os.getenv("PEXELS_API_KEY", "")
    if pexels_key:
        table.add_row("Image", "pexels", "[green]available[/green]", "API key set")
    else:
        table.add_row("Image", "pexels", "[yellow]no key[/yellow]", "Set PEXELS_API_KEY")

    console.print(table)
