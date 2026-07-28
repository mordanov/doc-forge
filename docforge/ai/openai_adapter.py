"""OpenAI implementation of AIProvider."""

from __future__ import annotations

import json

from openai import AsyncOpenAI, OpenAIError

from docforge.ai.base import (
    AIContext,
    AIProvider,
    AIProviderError,
    AIResponseValidationError,
    Prompt,
)
from docforge.ai.defaults import DefaultRenderingDecision
from docforge.core.rendering import RenderingDecision
from docforge.logging.setup import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(AIProvider):
    def __init__(self, api_key: str, max_retries: int = 3) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._max_retries = max_retries

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    def _temperature(self, creativity: int) -> float:
        creativity = max(1, min(10, creativity))
        return (creativity - 1) / 9.0

    async def generate(
        self,
        prompt: Prompt,
        context: AIContext,
        model: str = "gpt-4o",
        creativity: int = 5,
    ) -> RenderingDecision:
        from jinja2 import Template

        rendered_prompt = Template(prompt.template).render(**context.fields)
        temperature = self._temperature(creativity)
        include_temperature = temperature != 1.0
        retries_used = 0

        while retries_used < self._max_retries:
            try:
                kwargs: dict = {
                    "model": model,
                    "messages": [{"role": "user", "content": rendered_prompt}],
                    "response_format": {"type": "json_object"},
                }
                if include_temperature:
                    kwargs["temperature"] = temperature
                response = await self._client.chat.completions.create(**kwargs)
                raw = response.choices[0].message.content or ""
                data = json.loads(raw)
                return self._validate_and_build(data, context.chapter_id)
            except AIResponseValidationError:
                raise
            except OpenAIError as exc:
                error_str = str(exc)
                if (
                    include_temperature
                    and "unsupported_value" in error_str
                    and "temperature" in error_str
                ):
                    logger.warning(
                        "openai_temperature_unsupported",
                        model=model,
                        hint="model rejects non-default temperature; retrying without it",
                    )
                    include_temperature = False
                    continue
                retries_used += 1
                logger.warning(
                    "openai_attempt_failed",
                    attempt=retries_used,
                    max_retries=self._max_retries,
                    error=error_str,
                )
                if retries_used >= self._max_retries:
                    logger.error("openai_exhausted_retries", chapter_id=context.chapter_id)
                    return DefaultRenderingDecision.for_chapter(context.chapter_id)
            except Exception as exc:
                raise AIProviderError(self.provider_id, "unexpected_error", str(exc)) from exc

        return DefaultRenderingDecision.for_chapter(context.chapter_id)

    def _validate_and_build(self, data: dict, chapter_id: str) -> RenderingDecision:
        try:
            return RenderingDecision(chapter_id=chapter_id, **data)
        except Exception as exc:
            raise AIResponseValidationError(
                self.provider_id,
                str(data),
                f"Response does not match RenderingDecision schema: {exc}",
            ) from exc

    async def health_check(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except OpenAIError:
            return False
