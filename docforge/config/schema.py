"""Pydantic v2 configuration schema for DocForge."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIConfig(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4o"
    creativity: int = Field(default=5, ge=1, le=10)
    max_retries: int = Field(default=3, ge=1, le=10)
    prompt_set: str = "editorial_v1"

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_AI_")


class ImagesConfig(BaseSettings):
    enabled: bool = True
    policy: Literal["auto_search", "replace_placeholders", "preserve_existing", "disabled"] = (
        "auto_search"
    )
    sources: list[str] = Field(default_factory=lambda: ["wikimedia"])
    density: Literal["minimal", "balanced", "illustrated", "maximum"] = "balanced"
    max_file_size_mb: int = Field(default=15, ge=1, le=100)
    max_retries: int = Field(default=3, ge=1, le=10)
    # Extra regex patterns (case-insensitive) treated as image placeholder markers.
    # Matched against the full text of a paragraph. Add patterns here to handle
    # language- or template-specific conventions (e.g. "Фото \\d+" for Russian docs).
    extra_placeholder_patterns: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_IMAGES_")


class OutputConfig(BaseSettings):
    formats: list[str] = Field(default_factory=lambda: ["docx"])
    generate_cover: bool = True
    generate_toc: bool = True
    generate_page_numbers: bool = True
    generate_headers_footers: bool = True
    cover_style: Literal["auto", "photo", "minimal", "illustration", "none"] = "auto"
    toc_mode: Literal["generate", "update_existing", "keep_existing"] = "generate"
    headers_footers_mode: Literal["generate", "replace_existing", "keep_existing"] = "generate"

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_OUTPUT_")


class LoggingConfig(BaseSettings):
    level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["human", "json"] = "human"

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_LOG_")


class ServerConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    token_ttl_hours: int = Field(default=24, ge=1)
    upload_dir: Path = Path(".docforge/uploads")
    max_upload_mb: int = Field(default=50, ge=1, le=500)

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        return v


class CacheConfig(BaseSettings):
    dir: Path = Path(".docforge/cache")
    max_size_mb: int = Field(default=2048, ge=100)

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_CACHE_")


class ProjectConfig(BaseSettings):
    language: str = "en"
    template: str = "minimal"
    profile: str = "development"
    validation_level: Literal["fast", "standard", "strict"] = "standard"
    ai_explainability: Literal["off", "brief", "detailed"] = "off"
    offline: bool = False

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_PROJECT_")


class DocForgeConfig(BaseSettings):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    images: ImagesConfig = Field(default_factory=ImagesConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
