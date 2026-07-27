"""Image provider abstraction — base class and errors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from docforge.core.document import ImageCandidate


class ImageDownloadError(Exception):
    def __init__(self, provider: str, url: str, reason: str) -> None:
        super().__init__(f"{provider}: {reason} ({url})")
        self.provider = provider
        self.url = url
        self.reason = reason


class ImageLicenceError(Exception):
    def __init__(self, url: str, reported: str, actual: str) -> None:
        super().__init__(f"Licence mismatch for {url}: reported={reported}, actual={actual}")
        self.url = url
        self.reported = reported
        self.actual = actual


class ImageProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @property
    @abstractmethod
    def capabilities(self) -> list[str]: ...

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        orientation: str | None = None,
    ) -> list[ImageCandidate]:
        """
        Search for legally-licensed images.
        MUST only return candidates with ALLOWED licences (PD, CC0, CC BY, CC BY-SA).
        """
        ...

    @abstractmethod
    async def download(
        self,
        candidate: ImageCandidate,
        target_path: Path,
        max_width: int = 1920,
        max_height: int = 1080,
    ) -> Path:
        """
        Download and optimise image to target_path.
        Raises ImageDownloadError on failure after retries.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
