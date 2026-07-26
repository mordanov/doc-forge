"""Theme loader and inheritance resolver."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_THEMES_DIR = Path(__file__).parents[1] / "themes"
_THEME_CACHE: dict[str, dict] = {}


def load_theme(theme_id: str, themes_dir: Path | None = None) -> dict[str, Any]:
    """Load a theme YAML by id, resolving inheritance chain."""
    if theme_id in _THEME_CACHE:
        return _THEME_CACHE[theme_id]

    directory = themes_dir or _THEMES_DIR
    path = directory / f"{theme_id}.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Theme '{theme_id}' not found in {directory}")

    with open(path) as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    parent_id = data.get("inherits")
    if parent_id:
        parent = load_theme(parent_id, directory)
        data = _deep_merge(parent, data)

    _validate_theme(data, theme_id)
    _THEME_CACHE[theme_id] = data
    logger.debug("theme_loaded", id=theme_id)
    return data


def list_themes(themes_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = themes_dir or _THEMES_DIR
    themes = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            theme = load_theme(path.stem, directory)
            themes.append(theme)
        except Exception as exc:
            logger.warning("theme_load_failed", path=str(path), error=str(exc))
    return themes


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _validate_theme(data: dict[str, Any], theme_id: str) -> None:
    required = {"id", "version", "palette", "typography", "spacing"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Theme '{theme_id}' is missing required fields: {missing}")
