"""docforge CLI entry point — registers all sub-commands."""

from __future__ import annotations

import sys

import typer

from docforge.cli.analyse import analyse_command
from docforge.cli.cache import app as cache_app
from docforge.cli.clean import clean_command
from docforge.cli.config import config_command
from docforge.cli.doctor import doctor_command
from docforge.cli.export import export_command
from docforge.cli.init import init_command
from docforge.cli.prompts import prompts_command
from docforge.cli.providers import providers_command
from docforge.cli.render import render
from docforge.cli.server import app as server_app
from docforge.cli.themes import themes_command
from docforge.cli.validate import validate_command

app = typer.Typer(
    name="docforge",
    help="DocForge — AI-assisted editorial publishing pipeline.",
    no_args_is_help=True,
)

app.command("render")(render)
app.command("analyse")(analyse_command)
app.command("init")(init_command)
app.command("doctor")(doctor_command)
app.command("validate")(validate_command)
app.command("config")(config_command)
app.command("themes")(themes_command)
app.command("prompts")(prompts_command)
app.command("providers")(providers_command)
app.command("clean")(clean_command)
app.command("export")(export_command)
app.add_typer(cache_app, name="cache")
app.add_typer(server_app, name="server")


@app.command()
def version() -> None:
    """Print DocForge version and environment info."""
    import platform

    try:
        from importlib.metadata import version as pkg_version

        v = pkg_version("docforge")
    except Exception:
        v = "dev"
    typer.echo(f"DocForge {v}")
    typer.echo(f"Python {sys.version.split()[0]}")
    typer.echo(f"Platform {platform.platform()}")


if __name__ == "__main__":
    app()
