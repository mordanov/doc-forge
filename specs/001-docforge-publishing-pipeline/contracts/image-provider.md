# Image Provider Interface Contract

**Language**: Python 3.11+
**Module path**: `docforge.images.base`

---

## ImageProvider (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from docforge.core.document import ImageCandidate

class ImageProvider(ABC):

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier, e.g. 'wikimedia'."""

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """Must include at least: 'image_search', 'image_download'."""

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        orientation: str | None = None,   # 'landscape' | 'portrait' | 'square' | None
    ) -> list[ImageCandidate]:
        """
        Search for images matching query.
        Returns candidates sorted by provider relevance.
        MUST only return candidates with verified supported licences.
        MUST NOT return candidates with UNKNOWN or UNSUPPORTED licences.
        """

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
        Validates MIME type, extension, file integrity, and size limit.
        Returns resolved file path.
        Raises ImageDownloadError on failure — MUST NOT raise on transient errors
        without attempting retry (up to config.images.max_retries, default 3).
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is reachable and credentials are valid."""
```

## Errors

```python
class ImageDownloadError(Exception):
    provider: str
    url: str
    reason: str

class ImageLicenceError(Exception):
    """Raised when a downloaded image's actual licence differs from reported."""
    url: str
    reported: str
    actual: str
```

## Contract Rules

- `search()` MUST filter out any candidate whose licence is `UNKNOWN` or `UNSUPPORTED`.
- `download()` MUST validate:
  - MIME type is `image/jpeg`, `image/png`, or `image/webp`
  - File extension matches MIME type
  - File size ≤ `config.images.max_file_size_mb` (default 15 MB)
  - File is not corrupted (can be opened by Pillow)
- `download()` failure MUST NOT terminate the rendering pipeline; callers handle `ImageDownloadError` by retaining the placeholder.
- Provider MUST NEVER store credentials except via the config system (env vars).
- Attribution metadata (author, source page, licence, URL) MUST be preserved in `ImageCandidate` for the Image Sources appendix.
