# Research: DocForge Automated Publishing Pipeline

**Date**: 2026-07-26
**Branch**: `001-docforge-publishing-pipeline`

---

## 1. Python DOCX Library

**Decision**: `python-docx` (current stable release, ~0.8.x / 1.x)

**Rationale**: The only mature, actively maintained Python library for DOCX manipulation.
Provides programmatic access to paragraphs, runs, styles, tables, images, headers/footers,
sections, and page properties. Supports both reading and writing `.docx` files. Used in
production by many document automation tools.

**Alternatives considered**:
- `docx2python` — read-only, no write support.
- `docx-mailmerge` — merge-only, too narrow in scope.
- LibreOffice UNO API — requires a LibreOffice installation; heavy dependency; poor cross-platform CI.

**Key constraints**:
- DOCX styles must be defined in the document's `styles.xml`; programmatic style application
  requires either XML manipulation or pre-built style templates.
- Section properties (page size, margins, headers/footers) are per-section; the rendering
  engine must track section boundaries.
- Image insertion uses `add_picture()`; positioning within a paragraph requires inline or
  floating (anchored) placement via raw XML for advanced layouts.

---

## 2. HTTP Framework

**Decision**: FastAPI + Uvicorn

**Rationale**: FastAPI provides async-first request handling (matching the async Python API),
automatic OpenAPI/JSON Schema documentation, Pydantic v2 model validation (already a
dependency for config models), and excellent test support via `httpx.AsyncClient`. Uvicorn
is the standard ASGI server for FastAPI. Together they add minimal new dependencies.

**Alternatives considered**:
- Flask — synchronous; async support is bolted on; no automatic schema validation.
- aiohttp — lower-level; more boilerplate; no automatic docs.
- Django REST Framework — heavyweight; brings ORM and many unneeded components.

**Key decisions**:
- Long-running render jobs are queued via an in-process async task queue (Python
  `asyncio.Queue` + background worker) in v1; no external queue dependency (Celery/RQ).
- Job status is polled by the client; the server does not push updates (SSE/WebSocket
  deferred to v2).

---

## 3. AI Provider Abstraction

**Decision**: Abstract `AIProvider` base class; `OpenAIAdapter` as the sole v1 implementation.

**Rationale**: The spec mandates provider independence (Constitution §IV). A thin ABC with
`async def generate(prompt: Prompt, context: AIContext) -> RenderingDecision` is sufficient.
OpenAI's Python SDK (`openai>=1.0`) is async-compatible and stable.

**Model and creativity mapping**:
- `ai.model` → passed directly to the OpenAI `model` parameter.
- `ai.creativity` (1–10) → mapped to `temperature` linearly: `temperature = (creativity - 1) / 9.0`
  (1 → 0.0, 10 → 1.0). Documented in the adapter.

**Prompt storage**:
- Each prompt is a YAML file: `id`, `version`, `description`, `providers`, `template` (Jinja2
  string), `response_schema` (JSON Schema). Loaded at startup, validated against schema.

**Response validation**:
- All AI responses validated against Pydantic models derived from `response_schema`.
- On validation failure: retry up to `config.ai.max_retries` times (default 3).
- On exhausted retries: fall back to `DefaultRenderingDecision` (conservative layout).

**Caching**:
- Cache key: SHA-256 of `(prompt_id, prompt_version, serialised_context)`.
- Backend: same filesystem cache used for images; stored as JSON.

---

## 4. Image Provider Architecture

**Decision**: Abstract `ImageProvider` ABC; concrete adapters for Wikimedia Commons, Unsplash, Pexels.

**Wikimedia Commons**:
- Use the MediaWiki `action=query` API with `generator=search` and `prop=imageinfo`.
- Filter by `imageinfo.extmetadata.LicenseShortName` — accept: `Public Domain`, `CC0`, `CC BY`, `CC BY-SA`.
- No API key required; rate-limit to 1 req/s per Commons guidelines.

**Unsplash**:
- Use Unsplash API v1 (`/search/photos`). Requires `UNSPLASH_ACCESS_KEY`.
- All Unsplash photos are free-to-use under the Unsplash Licence (attribution required).
- Map to `CC BY` equivalent for attribution appendix.

**Pexels**:
- Use Pexels API v1 (`/v1/search`). Requires `PEXELS_API_KEY`.
- All Pexels photos are free under the Pexels Licence (attribution required).

**Candidate ranking** (configurable weights, defaults below):
```
licence_quality   : 0.40  (CC0/PD > CC BY > CC BY-SA)
resolution        : 0.25  (prefer ≥ 1200px wide)
orientation       : 0.20  (prefer landscape for body; portrait for cover)
relevance_score   : 0.15  (provider-returned relevance or rank)
```

**Download & optimisation**:
- `httpx.AsyncClient` for parallel downloads with timeout and retry.
- `Pillow` for resize, crop, colour profile normalisation (sRGB), JPEG compression.
- Max file size: 15 MB (configurable). Rejected formats: anything not JPEG/PNG/WEBP.

---

## 5. Local Project Store

**Decision**: SQLite via Python `sqlite3` stdlib; schema managed by hand-written migrations.

**Rationale**: Zero additional dependencies; SQLite is cross-platform, single-file,
and sufficient for single-user local storage. The project store is small (hundreds of rows
maximum for typical usage).

**Schema** (see data-model.md for full detail):
- `user_accounts` — single row in v1; username + bcrypt hash.
- `projects` — one row per job; JSON `config_snapshot` column.

**Alternatives considered**:
- SQLAlchemy — adds complexity; overkill for a single-user local store.
- SQLModel — interesting but young; introduces another dependency.
- JSON file — no query capability; fragile under concurrent writes (not a concern in v1
  but wrong architectural direction).

---

## 6. Authentication

**Decision**: Username/password via `.env`; bcrypt hashing; JWT session tokens.

**Flow**:
1. `docforge init` reads `DOCFORGE_USERNAME` and `DOCFORGE_PASSWORD` from `.env`,
   validates they are non-empty, hashes the password with bcrypt (work factor 12),
   and writes `(username, hashed_password)` to the `user_accounts` SQLite table.
2. `POST /auth/login` validates credentials against the stored hash; on success issues
   a JWT signed with `DOCFORGE_SECRET_KEY` (also from `.env`).
3. All other endpoints require `Authorization: Bearer <token>` header.
4. Token lifetime: 24 hours by default; configurable via `DOCFORGE_TOKEN_TTL_HOURS`.

**Libraries**:
- `bcrypt` for password hashing.
- `python-jose[cryptography]` for JWT encode/decode.
- FastAPI `Depends` for route-level auth guard.

**Security**:
- `DOCFORGE_SECRET_KEY` must be at least 32 characters; `docforge init` validates this.
- Password length minimum: 8 characters (validated at init time).
- Credentials never logged; sanitised error messages on auth failure (no username enumeration).

---

## 7. Configuration System

**Decision**: Pydantic v2 `BaseSettings` with YAML/TOML file loading + environment overrides.

**Precedence** (highest to lowest): CLI args → environment variables → project config file
  (`docforge.yaml` or `docforge.toml`) → built-in defaults.

**Libraries**:
- `pydantic-settings` for env-var loading and validation.
- `PyYAML` for YAML file parsing.
- `tomllib` (stdlib, Python 3.11+) for TOML parsing.
- `python-dotenv` for `.env` loading.

**Profiles**: YAML files under `docforge/config/profiles/`; a profile is a partial config
  that is merged into the base config. User specifies `--profile travel-guide`.

---

## 8. Logging

**Decision**: `structlog` with configurable output processors.

**Rationale**: `structlog` provides structured, context-aware logging with both
human-readable (dev) and JSON (production/CI) output modes. Integrates cleanly with FastAPI
and Python's stdlib `logging`. Supports bound loggers (per-request, per-job context).

**Levels**: TRACE (custom, 5) / DEBUG (10) / INFO (20) / WARNING (30) / ERROR (40) / CRITICAL (50).

---

## 9. Testing Strategy

**Decision**: pytest + pytest-asyncio + httpx for the full test pyramid.

| Layer | Tool | Scope |
|---|---|---|
| Unit | pytest | Pure domain logic; no I/O; 100% business logic coverage |
| Integration | pytest + httpx.AsyncClient | Real SQLite; mocked external providers |
| Rendering | pytest + python-docx | Pipeline produces valid DOCX structure |
| Golden | pytest | Byte/semantic comparison against fixture documents |
| E2E | pytest | Full CLI invocation against fixture documents |

**Visual snapshot tests**: rendered DOCX pages converted to PNG via LibreOffice headless
(available in CI) and compared with `Pillow` pixel diff. Threshold: configurable, default 2%.

**Static analysis**:
- `ruff` (linting + formatting)
- `mypy --strict` (type checking)
- `bandit` (security scanning)
- `pre-commit` hooks for all of the above

---

## 10. Dependency Summary

| Package | Purpose | Min Version |
|---|---|---|
| `python-docx` | DOCX read/write | 1.1+ |
| `fastapi` | HTTP API framework | 0.115+ |
| `uvicorn[standard]` | ASGI server | 0.30+ |
| `pydantic` | Data validation | 2.7+ |
| `pydantic-settings` | Config from env | 2.3+ |
| `httpx` | Async HTTP client (image downloads, provider APIs) | 0.27+ |
| `Pillow` | Image resize/optimise | 10.3+ |
| `openai` | OpenAI provider SDK | 1.30+ |
| `bcrypt` | Password hashing | 4.1+ |
| `python-jose[cryptography]` | JWT tokens | 3.3+ |
| `python-dotenv` | `.env` loading | 1.0+ |
| `PyYAML` | YAML config parsing | 6.0+ |
| `structlog` | Structured logging | 24.1+ |
| `typer[all]` | CLI framework | 0.12+ |
| `rich` | CLI output formatting | 13.7+ |

**Dev/test only**: `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `bandit`, `pre-commit`,
  `pytest-cov`, `respx` (httpx mock)
