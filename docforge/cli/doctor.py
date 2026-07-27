"""docforge doctor — environment readiness checks."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def doctor_command() -> None:
    """Check environment readiness for DocForge."""
    checks: list[tuple[str, str, str]] = []

    # Python version
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 11):
        checks.append(("Python version", f"{major}.{minor}", "PASS"))
    else:
        checks.append(("Python version", f"{major}.{minor} (need 3.11+)", "FAIL"))

    # Required packages
    for pkg in ["docx", "fastapi", "pydantic", "structlog", "typer", "PIL", "openai", "yaml"]:
        try:
            __import__(pkg)
            checks.append((f"Package: {pkg}", "installed", "PASS"))
        except ImportError:
            checks.append((f"Package: {pkg}", "missing", "FAIL"))

    # Cache directory writable
    cache_dir = Path.home() / ".docforge" / "cache"
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        test_file = cache_dir / ".write_test"
        test_file.write_text("ok")
        test_file.unlink()
        checks.append(("Cache dir writable", str(cache_dir), "PASS"))
    except Exception as exc:
        checks.append(("Cache dir writable", str(exc), "FAIL"))

    # Pillow available
    try:
        import PIL  # noqa: F401

        checks.append(("Pillow", "available", "PASS"))
    except ImportError:
        checks.append(("Pillow", "missing", "WARN"))

    table = Table(title="DocForge Doctor")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Result", justify="center")

    all_pass = True
    for name, status, result in checks:
        if result == "PASS":
            styled = "[green]PASS[/green]"
        elif result == "WARN":
            styled = "[yellow]WARN[/yellow]"
        else:
            styled = "[red]FAIL[/red]"
            all_pass = False
        table.add_row(name, status, styled)

    console.print(table)

    if all_pass:
        console.print("\n[green]All required checks passed.[/green]")
    else:
        console.print("\n[red]Some checks failed. Please resolve the issues above.[/red]")
        raise typer.Exit(1)
