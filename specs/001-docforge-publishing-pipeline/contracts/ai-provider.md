# AI Provider Interface Contract

**Language**: Python 3.11+
**Module path**: `docforge.ai.base`

---

## AIProvider (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from docforge.core.rendering import RenderingDecision
from docforge.ai.types import Prompt, AIContext

class AIProvider(ABC):

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier, e.g. 'openai'."""

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """List of model identifiers this provider supports."""

    @abstractmethod
    async def generate(
        self,
        prompt: Prompt,
        context: AIContext,
        model: str,
        creativity: int,   # 1–10; provider maps to its own temperature/sampling
    ) -> RenderingDecision:
        """
        Generate a rendering decision for a chapter.
        Raises AIProviderError on unrecoverable failure.
        Returns RenderingDecision validated against prompt.response_schema.
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and credentials are valid."""
```

## AIContext

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AIContext:
    chapter_id      : str
    chapter_title   : str
    nearby_text     : str      # First ~500 words of chapter
    placeholder_count: int
    template_name   : str
    language        : str
    page_dimensions : tuple[float, float]  # width, height in cm
    semantic_tags   : list[str]            # detected: location, landmark, etc.
```

## Prompt

```python
@dataclass(frozen=True)
class Prompt:
    id              : str
    version         : str
    description     : str
    providers       : list[str]
    template        : str          # Jinja2 template string
    response_schema : dict         # JSON Schema
    context_fields  : list[str]
```

## Errors

```python
class AIProviderError(Exception):
    """Raised on unrecoverable provider failure (after retries exhausted)."""
    provider: str
    code: str
    message: str

class AIResponseValidationError(AIProviderError):
    """Raised when the response does not match response_schema after all retries."""
    raw_response: str
```

## Contract Rules

- `generate()` MUST validate the response against `prompt.response_schema`.
- On validation failure, the adapter MUST retry internally (caller does not retry).
- After `config.ai.max_retries` failed attempts, MUST raise `AIResponseValidationError`.
- `generate()` MUST NEVER modify document state.
- Adapter MUST map `creativity` (1–10) to provider-native sampling parameter:
  `temperature = (creativity - 1) / 9.0`
- Cache key for response caching: `SHA-256(prompt.id + prompt.version + json(context))`.
