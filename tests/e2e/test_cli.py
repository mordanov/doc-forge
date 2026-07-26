"""E2E CLI test — invoke docforge render as subprocess."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SAMPLE_GUIDE = Path(__file__).parents[2] / "examples" / "sample-guide.docx"


@pytest.mark.skipif(not SAMPLE_GUIDE.exists(), reason="Sample fixture not found")
def test_docforge_render_cli_exits_zero():
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "cli_out.docx"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "docforge.cli.main",
                "render",
                str(SAMPLE_GUIDE),
                str(output),
                "--no-ai",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0


@pytest.mark.skipif(not SAMPLE_GUIDE.exists(), reason="Sample fixture not found")
def test_docforge_analyse_cli_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "docforge.cli.main", "analyse", str(SAMPLE_GUIDE)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_docforge_version_cli():
    result = subprocess.run(
        [sys.executable, "-m", "docforge.cli.main", "version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "DocForge" in result.stdout


def test_docforge_render_nonexistent_file_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "out.docx"
        result = subprocess.run(
            [sys.executable, "-m", "docforge.cli.main", "render", "nonexistent.docx", str(output)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
