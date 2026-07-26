"""AI provider abstraction — base class, types, and errors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from docforge.core.rendering import RenderingDecision


@dataclass(frozen=True)
class AIContext:
    chapter_id: str
    chapter_title: str
    nearby_text: str
    placeholder_count: int
    template_name: str
    language: str
    chapter_word_count: int = 0
    has_tables: bool = False
    has_images: bool = False
    page_dimensions: tuple[float, float] = (21.0, 29.7)  # A4 in cm
    semantic_tags: list[str] = field(default_factory=list)

    @property
    def fields(self) -> dict:
        import dataclasses

        return {f.name: getattr(self, f.name) for f in dataclasses.fields(self)}


@dataclass(frozen=True)
class Prompt:
    id: str
    version: str
    description: str
    providers: list[str]
    template: str
    response_schema: dict
    context_fields: list[str] = field(default_factory=list)


class AIProviderError(Exception):
    def __init__(self, provider: str, code: str, message: str) -> None:
        super().__init__(message)
        self.provider = provider
        self.code = code
        self.message = message


class AIResponseValidationError(AIProviderError):
    def __init__(self, provider: str, raw_response: str, message: str) -> None:
        super().__init__(provider, "validation_failed", message)
        self.raw_response = raw_response


class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @property
    @abstractmethod
    def supported_models(self) -> list[str]: ...

    @abstractmethod
    async def generate(
        self,
        prompt: Prompt,
        context: AIContext,
        model: str,
        creativity: int,
    ) -> RenderingDecision:
        """
        Generate a RenderingDecision for the given chapter context.
        Raises AIResponseValidationError after retries exhausted.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
