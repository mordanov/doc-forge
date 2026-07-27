"""docforge config — show resolved configuration."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax

from docforge.config.loader import load_config

console = Console()


def config_command(
    show_defaults: bool = typer.Option(False, "--show-defaults", help="Show built-in defaults"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text or json"),
    config: Path | None = typer.Option(None, "--config", help="Config file path"),
    profile: str | None = typer.Option(None, "--profile", help="Config profile"),
) -> None:
    """Show the active resolved configuration."""
    cfg = load_config(config_file=config, profile=profile)
    data = cfg.model_dump()

    if format == "json":
        console.print(json.dumps(data, indent=2, default=str))
        return

    import yaml

    rendered = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    console.print(Syntax(rendered, "yaml", theme="monokai"))
