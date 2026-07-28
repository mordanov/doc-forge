"""Prompt loader — load versioned YAML prompt files from the prompts/ directory."""

from __future__ import annotations

from pathlib import Path

import yaml

from docforge.ai.base import Prompt
from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_cache: dict[str, Prompt] = {}


def load_prompt(prompt_id: str, prompts_dir: Path | None = None) -> Prompt:
    if prompt_id in _cache:
        return _cache[prompt_id]

    search_dirs = [prompts_dir] if prompts_dir else []
    search_dirs.append(_default_prompts_dir())
    search_dirs.append(Path(__file__).parent / "builtin")

    for directory in search_dirs:
        path = directory / f"{prompt_id}.yaml"
        if path.exists():
            return _load_file(path)

    raise FileNotFoundError(f"Prompt '{prompt_id}' not found in {search_dirs}")


def _load_file(path: Path) -> Prompt:
    with open(path) as f:
        data = yaml.safe_load(f)

    prompt = Prompt(
        id=data["id"],
        version=data["version"],
        description=data.get("description", ""),
        providers=data.get("providers", []),
        template=data["template"],
        response_schema=data.get("response_schema", {}),
        context_fields=data.get("context_fields", []),
    )
    _cache[prompt.id] = prompt
    logger.debug("prompt_loaded", id=prompt.id, version=prompt.version)
    return prompt


def list_prompts(prompts_dir: Path | None = None) -> list[Prompt]:
    directory = prompts_dir or _default_prompts_dir()
    prompts = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            prompts.append(_load_file(path))
        except Exception as exc:
            logger.warning("prompt_load_failed", path=str(path), error=str(exc))
    return prompts


def _default_prompts_dir() -> Path:
    return Path(__file__).parents[3] / "prompts"
