# Plugin Manifest Schema

Every DocForge plugin MUST include a `plugin.yaml` manifest at its package root.

## Schema

```yaml
id: wikimedia                          # Unique identifier (lowercase, hyphens only)
name: Wikimedia Commons                # Human-readable name
version: 1.0.0                         # Semver
author: DocForge                       # Author name or organisation
api_version: 1                         # Plugin API contract version (integer)
entrypoint: docforge.plugins.wikimedia # Python module path; must export `plugin` symbol
license: MIT                           # SPDX licence identifier

capabilities:                          # At least one required
  - image_search
  - image_download

# Optional: minimum DocForge version required
requires_docforge: ">=1.0.0"

# Optional: additional Python dependencies
dependencies:
  - httpx>=0.27
```

## Supported capability values

| Capability | Description |
|---|---|
| `image_search` | Provider can search for image candidates |
| `image_download` | Provider can download and optimise images |
| `ai_generate` | Provider can generate rendering decisions |
| `export` | Provider can export to an output format |
| `analyse` | Provider can analyse document structure |
| `validate` | Provider can run validation checks |
| `post_process` | Provider can post-process a rendered document |
| `metadata` | Provider can supply document metadata |

## Plugin entrypoint contract

The `entrypoint` module MUST export a `plugin` symbol that is an instance of the
appropriate base class (`ImageProvider`, `AIProvider`, etc.).

```python
# docforge/plugins/wikimedia/__init__.py
from docforge.images.base import ImageProvider
from .provider import WikimediaProvider

plugin: ImageProvider = WikimediaProvider()
```

## Lifecycle

Plugins are discovered at startup from:
1. Built-in plugins in `docforge/plugins/`
2. Installed packages with entry point group `docforge.plugins`

Lifecycle: **Discovery → Manifest Validation → Registration → Initialisation → Execution → Shutdown**

Initialisation failure of an optional plugin logs a warning and continues.
Initialisation failure of a required plugin (e.g., the active AI provider) stops execution.

## Contract Rules

- Plugins MUST NOT communicate directly with other plugins.
- Plugins MUST NOT access internal application state beyond the public extension API.
- Plugins MUST NOT contain executable logic in their manifest YAML.
- `api_version` mismatch (plugin > host) MUST raise a clear error at registration time.
