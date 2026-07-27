"""Plugin manifest schema."""

from __future__ import annotations

from pydantic import BaseModel, Field

SUPPORTED_CAPABILITIES = frozenset(
    {
        "image_search",
        "image_download",
        "ai_generate",
        "export",
        "analyse",
        "validate",
        "post_process",
        "metadata",
    }
)


class PluginManifest(BaseModel):
    id: str
    name: str
    version: str
    author: str = ""
    api_version: int = 1
    entrypoint: str
    capabilities: list[str] = Field(default_factory=list)
    license: str = "MIT"
    requires_docforge: str | None = None
    dependencies: list[str] = Field(default_factory=list)

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities
