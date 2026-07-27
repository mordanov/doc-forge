"""Plugin registry — discovery, validation, and lifecycle management."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import yaml

from docforge.logging.setup import get_logger
from docforge.plugins.manifest import PluginManifest

logger = get_logger(__name__)

HOST_API_VERSION = 1


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, tuple[PluginManifest, Any]] = {}

    def register(self, manifest: PluginManifest, instance: Any) -> None:
        if manifest.api_version > HOST_API_VERSION:
            raise ValueError(
                f"Plugin '{manifest.id}' requires API v{manifest.api_version} "
                f"but host supports v{HOST_API_VERSION}"
            )
        self._plugins[manifest.id] = (manifest, instance)
        logger.info("plugin_registered", plugin_id=manifest.id, version=manifest.version)

    def get(self, plugin_id: str) -> Any | None:
        entry = self._plugins.get(plugin_id)
        return entry[1] if entry else None

    def list_by_capability(self, capability: str) -> list[tuple[PluginManifest, Any]]:
        return [(m, p) for m, p in self._plugins.values() if m.has_capability(capability)]

    def load_from_directory(self, plugins_dir: Path) -> None:
        for manifest_path in plugins_dir.glob("*/plugin.yaml"):
            try:
                with open(manifest_path) as f:
                    data = yaml.safe_load(f)
                manifest = PluginManifest(**data)
                module = importlib.import_module(manifest.entrypoint)
                instance = module.plugin
                self.register(manifest, instance)
            except Exception as exc:
                logger.warning(
                    "plugin_load_failed",
                    path=str(manifest_path),
                    error=str(exc),
                )

    @property
    def all(self) -> dict[str, tuple[PluginManifest, Any]]:
        return dict(self._plugins)


_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    return _registry
