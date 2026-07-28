"""PDF exporter — converts a DOCX file to PDF via docx2pdf (LibreOffice fallback)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from docforge.logging.setup import get_logger

logger = get_logger(__name__)


def export(docx_path: Path, output_path: Path) -> Path:
    """Convert docx_path to PDF at output_path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Try docx2pdf first (cross-platform, uses Word on macOS/Windows)
    try:
        from docx2pdf import convert

        convert(str(docx_path), str(output_path))
        logger.info("pdf_exported_docx2pdf", path=str(output_path))
        return output_path
    except ImportError:
        logger.debug("docx2pdf_not_installed", hint="Falling back to LibreOffice")
    except Exception as exc:
        logger.warning("docx2pdf_failed", error=str(exc), hint="Trying LibreOffice")

    # Fallback: LibreOffice headless
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_path.parent),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice PDF conversion failed: {result.stderr.strip()}\n"
            "Install docx2pdf or LibreOffice to enable PDF export."
        )

    # LibreOffice writes <stem>.pdf next to the input file; rename if needed
    lo_output = output_path.parent / f"{docx_path.stem}.pdf"
    if lo_output.exists() and lo_output != output_path:
        lo_output.rename(output_path)

    logger.info("pdf_exported_libreoffice", path=str(output_path))
    return output_path
