"""Configuration loader: .env → YAML/TOML file → env vars → defaults."""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml
from dotenv import load_dotenv

from docforge.config.schema import DocForgeConfig


def load_config(
    config_file: Path | None = None,
    profile: str | None = None,
) -> DocForgeConfig:
    """
    Load configuration from environment and optional YAML/TOML file.

    Precedence (highest to lowest):
      1. Environment variables
      2. config_file (YAML or TOML)
      3. Profile YAML (built-in preset)
      4. Built-in defaults
    """
    load_dotenv(override=False)

    overrides: dict = {}

    if config_file is not None:
        overrides = _load_file(config_file)

    if profile:
        profile_path = _find_profile(profile)
        if profile_path and profile_path.exists():
            profile_data = _load_file(profile_path)
            # Config file values take precedence over profile
            overrides = _deep_merge(profile_data, overrides)

    # DocForgeConfig reads env vars automatically via pydantic-settings
    # Pass file-based overrides as initial values; env vars still win
    return DocForgeConfig(**overrides)


def _load_file(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    if suffix == ".toml":
        with open(path, "rb") as fb:
            return tomllib.load(fb)
    raise ValueError(f"Unsupported config file format: {suffix}")


def _find_profile(profile: str) -> Path | None:
    profiles_dir = Path(__file__).parent / "profiles"
    for ext in ("yaml", "yml"):
        candidate = profiles_dir / f"{profile}.{ext}"
        if candidate.exists():
            return candidate
    return None


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
