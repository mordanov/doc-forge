"""DocForge — AI-assisted editorial publishing platform."""

from __future__ import annotations

from docforge.core.rendering import RenderingDecision
from docforge.renderer import Renderer
from docforge.rendering.report import RenderingReport

__version__ = "1.0.0"

__all__ = ["Renderer", "RenderingDecision", "RenderingReport", "__version__"]
