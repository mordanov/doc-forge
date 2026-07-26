---
description: "Task list for DocForge Automated Publishing Pipeline"
---

# Tasks: DocForge Automated Publishing Pipeline

**Input**: Design documents from `specs/001-docforge-publishing-pipeline/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, tooling, and dependency configuration.

- [ ] T001 Create Python package structure per plan.md (`docforge/`, `tests/`, `prompts/`, `docs/`, `examples/`, `scripts/`)
- [ ] T002 Create `pyproject.toml` with all dependencies from research.md dependency table
- [ ] T003 [P] Configure Ruff (linting + formatting) in `pyproject.toml`
- [ ] T004 [P] Configure MyPy (strict) in `pyproject.toml`
- [ ] T005 [P] Configure Bandit in `pyproject.toml`
- [ ] T006 [P] Configure pre-commit hooks in `.pre-commit-config.yaml`
- [ ] T007 [P] Configure pytest and pytest-asyncio in `pyproject.toml`
- [ ] T008 Create `.env.example` with all required variables (`DOCFORGE_USERNAME`, `DOCFORGE_PASSWORD`, `DOCFORGE_SECRET_KEY`, `OPENAI_API_KEY`, `UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`)
- [ ] T009 [P] Create `.gitignore` excluding `.env`, `__pycache__`, `.mypy_cache`, `dist/`, `cache/`, `*.docx` output files
- [ ] T010 Create `docforge/__init__.py` with package version constant and public `Renderer` re-export

**Checkpoint**: Package structure exists; `pip install -e .` succeeds; linting tools run without error on empty package.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T011 Create Pydantic v2 domain models for `SemanticModel` and all element types in `docforge/core/document.py` (Document, Section, Chapter, Paragraph, Heading, Table, Row, Cell, ImagePlaceholder, Image, Caption, Sidebar, PageBreak, Header, Footer, Appendix, DocumentStatistics)
- [ ] T012 [P] Create `RenderingDecision`, `RenderingJob`, `RenderEstimate`, `ValidationSummary`, `LicenceSummary`, `ValidationIssue`, `JobStatus`, `RenderStage` models in `docforge/core/rendering.py`
- [ ] T013 [P] Create `Project`, `UserAccount` Pydantic models in `docforge/core/project.py`
- [ ] T014 Create Pydantic v2 `BaseSettings` config schema in `docforge/config/schema.py` covering all configuration sections (project, ai, images, output, logging, server, cache) with defaults and validators
- [ ] T015 Implement config loader in `docforge/config/loader.py`: reads `.env`, YAML/TOML file, merges with env vars and built-in defaults per precedence order from FR-020
- [ ] T016 [P] Create built-in configuration profiles as YAML files in `docforge/config/profiles/` (development, production, ci, offline, travel-guide, book, report)
- [ ] T017 Implement SQLite database setup in `docforge/server/store.py`: create tables (`user_accounts`, `jobs`, `projects`) with schema from data-model.md DDL; implement idempotent `init_db()` function
- [ ] T018 [P] Implement structured logging setup in `docforge/logging/setup.py` using `structlog`: configurable level, human-readable dev mode, JSON production mode; bind job_id context where applicable
- [ ] T019 Create `AIProvider` ABC, `AIContext`, `Prompt`, `AIProviderError`, `AIResponseValidationError` in `docforge/ai/base.py` per contracts/ai-provider.md
- [ ] T020 [P] Create `ImageProvider` ABC, `ImageDownloadError`, `ImageLicenceError` in `docforge/images/base.py` per contracts/image-provider.md
- [ ] T021 [P] Create `PluginManifest` Pydantic model and plugin registry skeleton in `docforge/plugins/registry.py` and `docforge/plugins/manifest.py` per contracts/plugin-manifest.md
- [ ] T022 Implement filesystem cache backend in `docforge/cache/filesystem.py`: store/retrieve by SHA-256 key; JSON sidecar for metadata; separate buckets for images and AI responses; implement `CacheBase` ABC in `docforge/cache/base.py`

**Checkpoint**: All domain models import cleanly; config loader reads `.env`; SQLite tables create successfully; logging emits structured output; all ABCs importable.

---

## Phase 3: User Story 1 — Document Rendering (Priority: P1) 🎯 MVP

**Goal**: A user can run `docforge render input.docx output.docx` and receive a publication-quality DOCX with styled content, sourced images, cover, TOC, headers/footers, and Image Sources appendix.

**Independent Test**: Run `docforge render examples/sample-guide.docx output/test.docx --template minimal --language en`; verify output file is non-empty, valid DOCX, contains cover section, TOC, and Image Sources appendix.

### Implementation for User Story 1

- [ ] T023 [P] [US1] Implement `DocumentLoader` in `docforge/document/loader.py`: open `.docx` with python-docx, build `Document` domain model; MUST NOT modify source file (FR-002)
- [ ] T024 [P] [US1] Implement `DocumentAnalyser` in `docforge/document/analyser.py`: traverse loaded Document, produce `SemanticModel` with chapters, elements, placeholders, and `DocumentStatistics`
- [ ] T025 [US1] Implement `OpenAIAdapter` in `docforge/ai/openai_adapter.py`: implement `AIProvider` ABC; map `creativity` (1–10) to temperature; validate responses against `prompt.response_schema`; retry up to `max_retries`; fall back to `DefaultRenderingDecision` on exhausted retries (FR-018, FR-019a)
- [ ] T026 [P] [US1] Implement `DefaultRenderingDecision` fallback in `docforge/ai/defaults.py`: returns a conservative `RenderingDecision` used when AI fails or is disabled
- [ ] T027 [US1] Implement prompt loader in `docforge/ai/prompts/loader.py`: load versioned prompt YAML files from `prompts/` directory; validate schema; cache in memory; implement `editorial_v1` prompt as the first prompt YAML in `prompts/editorial_v1.yaml`
- [ ] T028 [US1] Implement AI response cache in `docforge/ai/cache.py`: SHA-256 key from `(prompt_id, prompt_version, serialised_context)`; delegate to `CacheBase`; implement cache lookup before calling provider (FR-019)
- [ ] T029 [P] [US1] Implement `WikimediaProvider` in `docforge/images/wikimedia.py`: search via MediaWiki API; filter for supported licences only; rate-limit to 1 req/s; implement `health_check()`
- [ ] T030 [P] [US1] Implement image downloader in `docforge/images/downloader.py`: parallel async downloads via `httpx.AsyncClient`; validate MIME type, extension, file integrity, size limit; retry up to `max_retries`; handle `ImageDownloadError` without terminating pipeline (FR-014)
- [ ] T031 [P] [US1] Implement image optimiser in `docforge/images/optimiser.py` using Pillow: resize, crop, sRGB normalisation, JPEG compression; preserve attribution metadata
- [ ] T032 [US1] Implement image cache in `docforge/images/cache.py`: filesystem backend; cache key = SHA-256 of `(url, checksum, dimensions, licence)`; JSON sidecar with provenance metadata (FR-013)
- [ ] T033 [US1] Implement licence validator in `docforge/images/licence.py`: classify `LicenceType`; reject `UNKNOWN`/`UNSUPPORTED`; log warning on unverified licence (FR-012)
- [ ] T034 [P] [US1] Implement `MinimalTheme` YAML definition in `docforge/themes/minimal.yaml`; implement theme loader in `docforge/templates/engine.py`: load and validate theme YAML; resolve inheritance chain
- [ ] T035 [US1] Implement `RenderingEngine` in `docforge/rendering/engine.py`: consume `SemanticModel` + `Theme` + `RenderingDecision` list; apply styles via python-docx; insert images with captions; generate cover, TOC, headers/footers, Image Sources appendix (FR-004–FR-011)
- [ ] T036 [US1] Implement `LayoutValidator` in `docforge/rendering/layout_validator.py`: check heading hierarchy, page breaks, orphan headings, widow paragraphs, oversized images, caption placement, table overflow, section consistency; return `ValidationSummary` (FR-008)
- [ ] T037 [US1] Implement `RenderingReport` builder in `docforge/rendering/report.py`: collect recovered errors, skipped operations, warnings, fatal failures, suggested actions, image attributions, duration
- [ ] T038 [US1] Implement DOCX exporter in `docforge/exporters/docx.py`: write final `SemanticModel` to `.docx` via python-docx; validate output is valid DOCX; write document metadata (title, author, keywords, language, generation timestamp, template, DocForge version)
- [ ] T039 [US1] Implement `docforge render` CLI command in `docforge/cli/render.py` using Typer: accept input/output paths + all config flags; display progress per stage; exit 0 on success, non-zero on fatal error; implement `--verbose` flag (FR-023, FR-035)
- [ ] T040 [US1] Wire full render pipeline in `docforge/core/pipeline.py`: Loader → Analyser → AI Engine → Image Pipeline → Theme → Renderer → Validator → Exporter; implement as composable async pipeline with stage callbacks for progress reporting

**Checkpoint**: `docforge render examples/sample-guide.docx output/test.docx` completes; output DOCX is valid, non-empty, contains all mandatory sections; Image Sources appendix present with at least one entry.

---

## Phase 4: User Story 2 — Document Analysis (Priority: P2)

**Goal**: A user can run `docforge analyse input.docx` and receive a structured report of document structure, placeholders, and issues — without any file modification.

**Independent Test**: Run `docforge analyse examples/sample-guide.docx`; verify source file is unmodified (checksum match before/after); verify report lists chapters, placeholders, tables, and issues.

### Implementation for User Story 2

- [ ] T041 [P] [US2] Implement `docforge analyse` CLI command in `docforge/cli/analyse.py`: print structured report (chapters, headings, image placeholders, tables, detected issues, statistics); support `--format json` for machine-readable output; source file MUST remain unmodified (FR-002)
- [ ] T042 [US2] Implement issue detector in `docforge/document/analyser.py` (extend T024): detect orphan headings, missing captions, broken references, duplicate identifiers, malformed tables; each issue carries `code`, `message`, `location`

**Checkpoint**: `docforge analyse examples/sample-guide.docx` produces report; source file checksum unchanged; `--format json` produces parseable JSON.

---

## Phase 5: User Story 3 — Configuration & Theme Selection (Priority: P2)

**Goal**: A user can configure rendering through a YAML config file or CLI flags; invalid config stops execution with a clear error.

**Independent Test**: Render with `docforge.yaml` specifying `template: minimal` and `language: ru`; verify output uses Minimal theme and Russian auto-generated text; render with invalid config and verify non-zero exit with descriptive error.

### Implementation for User Story 3

- [ ] T043 [P] [US3] Create built-in theme YAML definitions: `national_geographic.yaml`, `lonely_planet.yaml`, `dk_eyewitness.yaml`, `corporate.yaml` in `docforge/themes/`; each must expose the full theme configuration surface
- [ ] T044 [P] [US3] Implement theme inheritance resolver in `docforge/templates/engine.py` (extend T034): merge child theme over parent; validate all required fields present after merge
- [ ] T045 [US3] Implement i18n string tables for all auto-generated text (TOC label, Figure, Table, Image Sources, Page, Appendix) in `docforge/core/i18n.py` for: Russian, English, Spanish, German, French (FR-030–FR-032)
- [ ] T046 [US3] Implement language-specific typography rules in `docforge/rendering/typography.py`: quotation marks, punctuation spacing, date formats, list formatting per language (FR-032)
- [ ] T047 [US3] Implement `docforge config` CLI command in `docforge/cli/config.py`: show active resolved configuration; support `--show-defaults` and `--format json`
- [ ] T048 [US3] Implement `docforge themes` CLI command in `docforge/cli/themes.py`: list available themes with id, name, version, description

**Checkpoint**: Render with `--template national_geographic --language ru` produces output with Russian labels; invalid `--template nonexistent` produces non-zero exit with helpful message.

---

## Phase 6: User Story 4 — Validation & Doctor (Priority: P3)

**Goal**: A user can run `docforge validate` and `docforge doctor` to verify environment readiness and configuration correctness before rendering.

**Independent Test**: Run `docforge doctor` in a correctly configured environment — all required checks pass; run `docforge validate --config bad.yaml` — exits non-zero with specific error identifying the invalid field.

### Implementation for User Story 4

- [ ] T049 [P] [US4] Implement `docforge doctor` command in `docforge/cli/doctor.py`: check Python version, installed dependencies, user account provisioned, AI provider credentials, internet connectivity, cache directory writable, fonts, Pillow available; structured pass/fail/warn output (FR-025)
- [ ] T050 [US4] Implement `docforge validate` command in `docforge/cli/validate.py`: validate configuration file, template schema, prompt files, provider credentials, document structure (if `--document` path provided); produce structured report; exit non-zero on any error (FR-021)

**Checkpoint**: `docforge doctor` passes all required checks in a configured environment; `docforge validate --config examples/docforge.yaml` exits 0; `docforge validate --config invalid.yaml` exits non-zero with field-level error.

---

## Phase 7: User Story 5 — Python API Integration (Priority: P3)

**Goal**: A developer can call `Renderer().render(input, output)` and receive the same result as the CLI.

**Independent Test**: Python script calling `Renderer().template("minimal").language("en").render("examples/sample-guide.docx", "output/api-test.docx")` produces a valid output file identical in structure to the CLI equivalent.

### Implementation for User Story 5

- [ ] T051 [US5] Implement `Renderer` public API class in `docforge/renderer.py`: fluent builder pattern (`.template()`, `.language()`, `.provider()`, `.model()`, `.creativity()`); both sync `render()` and async `arender()` methods; type annotations on all public methods; implemented using the same internal pipeline as the CLI (FR-027–FR-029)
- [ ] T052 [P] [US5] Expose `Renderer` and key public types (`RenderingReport`, `RenderingDecision`, `Theme`) from `docforge/__init__.py`; verify `from docforge import Renderer` works after `pip install`

**Checkpoint**: `python -c "from docforge import Renderer; Renderer().render('examples/sample-guide.docx', 'output/api.docx')"` succeeds; output matches CLI output.

---

## Phase 8: User Story — HTTP API & Project Store (from Clarifications)

**Goal**: A user can start a local HTTP server, authenticate, upload a document, submit a rendering job, poll for status, download the result, and manage past projects via REST API.

**Independent Test**: Full quickstart.md HTTP API section executes successfully end-to-end; project appears in `GET /projects`; output file downloads cleanly.

### Implementation for User Story HTTP

- [ ] T053 [P] [USHTTP] Implement `docforge init` CLI command in `docforge/cli/init.py`: read `DOCFORGE_USERNAME`, `DOCFORGE_PASSWORD`, `DOCFORGE_SECRET_KEY` from `.env`; validate non-empty and minimum length; hash password with bcrypt (work factor 12); write to `user_accounts` table; idempotent (`--force` to overwrite) (FR-047–049, FR-023a)
- [ ] T054 [P] [USHTTP] Implement auth module in `docforge/server/auth.py`: `POST /auth/login` endpoint; bcrypt verification; JWT issue with `python-jose`; `Depends` auth guard for all protected routes; token TTL from config (FR-050–051)
- [ ] T055 [USHTTP] Implement FastAPI application in `docforge/server/app.py`: mount all routers; startup event runs `init_db()`; startup guard checks user account exists before serving protected routes; returns `503` with init instructions if not initialised (FR-049)
- [ ] T056 [USHTTP] Implement document upload and analysis router in `docforge/server/routers/documents.py`: `POST /documents/upload` (multipart, 50 MB limit, `.docx` only); `POST /documents/{id}/analyse` (calls DocumentAnalyser, returns stats + issues); uploaded files stored in configurable `upload_dir` (FR-038)
- [ ] T057 [USHTTP] Implement async job queue in `docforge/server/jobs.py`: `asyncio.Queue` + background worker task started at server startup; job lifecycle: QUEUED → RUNNING → COMPLETED/FAILED; stage and progress callbacks update SQLite row (FR-041)
- [ ] T058 [USHTTP] Implement jobs router in `docforge/server/routers/jobs.py`: `POST /jobs` (submit job, returns 202); `GET /jobs/{id}` (poll status + report on completion); `GET /jobs/{id}/download/{format}` (stream output file); `DELETE /jobs/{id}` (cancel/delete); `POST /jobs/estimate` (dry-run estimate without rendering) (FR-038–042a)
- [ ] T059 [USHTTP] Implement project store CRUD in `docforge/server/store.py` (extend T017): save Project on job completion; list/detail/duplicate/delete operations; duplication creates a new job payload with config snapshot (FR-043–046)
- [ ] T060 [USHTTP] Implement projects router in `docforge/server/routers/projects.py`: `GET /projects` (paginated list); `GET /projects/{id}` (detail with config snapshot); `POST /projects/{id}/duplicate` (new job from snapshot); `DELETE /projects/{id}` (delete record + output files, preserve input) (FR-044, FR-046)
- [ ] T061 [P] [USHTTP] Implement system router in `docforge/server/routers/system.py`: `GET /system/health`; `GET /system/themes`; `GET /system/providers` (AI and image provider availability)
- [ ] T062 [USHTTP] Implement `docforge server` CLI command group in `docforge/cli/server.py`: `start` (launches Uvicorn with config); `stop` (graceful shutdown via PID file); `status` (reports running/stopped + port)
- [ ] T063 [P] [USHTTP] Implement `docforge` CLI entry point in `docforge/cli/main.py`: register all sub-commands (render, analyse, init, doctor, validate, config, themes, cache, prompts, providers, version, export, images, clean, server); configure root command with `--config`, `--profile`, `--verbose`, `--format` global flags

**Checkpoint**: Full quickstart.md HTTP API section runs end-to-end; all `curl` commands produce expected responses; `GET /projects` lists the completed job.

---

## Phase 9: Additional Image Providers (Priority: P3)

**Goal**: Unsplash and Pexels providers available as alternatives to Wikimedia.

**Independent Test**: Configure `image.sources: [unsplash]` with valid API key; render a document; verify at least one image sourced from Unsplash appears in Image Sources appendix.

- [ ] T064 [P] [USIMG] Implement `UnsplashProvider` in `docforge/images/unsplash.py`: search via Unsplash API v1; map licence to `CC_BY`; require `UNSPLASH_ACCESS_KEY`
- [ ] T065 [P] [USIMG] Implement `PexelsProvider` in `docforge/images/pexels.py`: search via Pexels API v1; map licence to `CC_BY`; require `PEXELS_API_KEY`
- [ ] T066 [P] [USIMG] Implement candidate ranker in `docforge/images/ranker.py`: weighted scoring (licence 40%, resolution 25%, orientation 20%, relevance 15%); configurable weights; returns ranked `list[ImageCandidate]`

**Checkpoint**: `--image-sources unsplash` produces images sourced from Unsplash with correct attribution in appendix.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, documentation, and hardening across all stories.

- [ ] T067 [P] Write unit tests for all domain models in `tests/unit/test_models.py` (Document, SemanticModel, RenderingDecision, Project, UserAccount, RenderEstimate)
- [ ] T068 [P] Write unit tests for config loader in `tests/unit/test_config.py`: precedence order, validation errors, profile merging
- [ ] T069 [P] Write unit tests for licence validator in `tests/unit/test_licence.py`: all licence type classifications; rejection of UNKNOWN/UNSUPPORTED
- [ ] T070 [P] Write unit tests for AI response validation and fallback in `tests/unit/test_ai.py`: schema validation pass/fail, retry exhaustion → DefaultRenderingDecision
- [ ] T071 [P] Write unit tests for image candidate ranker in `tests/unit/test_ranker.py`
- [ ] T072 Write integration tests for SQLite store in `tests/integration/test_store.py`: job lifecycle, project CRUD, user account creation (real SQLite, no mocks)
- [ ] T073 Write integration tests for HTTP API in `tests/integration/test_api.py` using `httpx.AsyncClient`: auth flow, document upload, job submit+poll+download, project CRUD, estimation endpoint
- [ ] T074 Write rendering tests in `tests/rendering/test_pipeline.py`: full pipeline against `tests/golden/fixtures/sample-guide.docx`; verify output DOCX contains cover, TOC, Image Sources appendix
- [ ] T075 Write golden document tests in `tests/golden/test_golden.py`: compare rendered output against `tests/golden/fixtures/expected-output.docx` by page count, heading hierarchy, style names, caption presence, image attribution entries
- [ ] T076 Write e2e CLI test in `tests/e2e/test_cli.py`: invoke `docforge render` as subprocess; verify exit 0 and output file existence
- [ ] T077 [P] Add `examples/sample-guide.docx` fixture (a minimal 10-page DOCX with 3 chapters, 2 tables, 4 image placeholders) and `examples/docforge.yaml` sample config
- [ ] T078 [P] Implement `docforge cache` CLI command in `docforge/cli/cache.py`: `list` (show cached items + sizes), `clear` (purge all or by type), `stats` (total size, item count)
- [ ] T079 [P] Implement `docforge prompts` CLI command in `docforge/cli/prompts.py`: list loaded prompts with id, version, description, supported providers
- [ ] T080 [P] Implement `docforge providers` CLI command in `docforge/cli/providers.py`: list all registered AI and image providers with availability status and reason
- [ ] T081 [P] Implement `docforge version` CLI command in `docforge/cli/version.py`: print `DocForge {version}`, Python version, platform
- [ ] T082 [P] Implement `docforge clean` CLI command in `docforge/cli/clean.py`: remove temporary files, purge old job outputs per retention policy
- [ ] T083 Add `docforge export` CLI command stub in `docforge/cli/export.py` with `--format` flag; for v1 only `docx` supported; stub other formats with "not available in v1.0" message
- [ ] T084 [P] Write `docs/quickstart.md` from `specs/001-docforge-publishing-pipeline/quickstart.md`; validate all commands in it produce documented output
- [ ] T085 [P] Verify all public API methods have type annotations; run `mypy --strict docforge/` with zero errors
- [ ] T086 [P] Run `ruff check docforge/ tests/` and `ruff format --check docforge/ tests/` with zero violations
- [ ] T087 [P] Run `bandit -r docforge/` with zero critical/high issues
- [ ] T088 Run quickstart.md full validation checklist from `specs/001-docforge-publishing-pipeline/quickstart.md`; all items pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 Rendering (Phase 3)**: Depends on Phase 2 — core value delivery
- **US2 Analysis (Phase 4)**: Depends on T024 (Analyser from Phase 3) — T024 must be complete
- **US3 Config/Themes (Phase 5)**: Depends on Phase 2 + T034 (Theme loader from Phase 3)
- **US4 Validation (Phase 6)**: Depends on Phase 2; can start alongside US1
- **US5 Python API (Phase 7)**: Depends on Phase 3 (full pipeline)
- **HTTP API (Phase 8)**: Depends on Phase 3 (pipeline) + Phase 2 (store/auth infra)
- **Image Providers (Phase 9)**: Depends on T029–T033 (image pipeline from Phase 3)
- **Polish (Phase 10)**: Depends on all desired stories being complete

### Within Each Phase (Sequential Order)

- T011 → T012, T013 (models first, then rendering + project models)
- T014 → T015, T016 (schema before loader)
- T017 → T022 (DB setup before cache)
- T023 → T024 (Loader before Analyser)
- T024 → T025 (Analyser before AI adapter — needs SemanticModel)
- T025, T026, T027, T028 → T035 (AI layer before Renderer)
- T029, T030, T031, T032, T033 → T035 (Image pipeline before Renderer)
- T034 → T035 (Theme before Renderer)
- T035, T036, T037, T038 → T039, T040 (full engine before CLI wiring)

### Parallel Opportunities (Selected)

```bash
# Phase 2 — run together after T011:
T012 (rendering models) || T013 (project models) || T018 (logging) || T019 (AI ABC) || T020 (Image ABC) || T021 (plugin registry)

# Phase 3 — run together after Foundational:
T023 (Loader) || T029 (Wikimedia) || T034 (Minimal theme)

# Phase 3 — run together after T023:
T024 (Analyser) || T030 (Downloader) || T031 (Optimiser) || T032 (Image cache) || T033 (Licence validator)

# Phase 3 — run together after T024 + image pipeline:
T025 (OpenAI adapter) || T026 (Defaults) || T027 (Prompt loader)

# Phase 8 — run together after Phase 3 + Foundational:
T053 (init command) || T054 (auth module) || T061 (system router) || T063 (CLI entry point)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 Document Rendering (T023–T040)
4. **STOP and VALIDATE**: Run `docforge render examples/sample-guide.docx output/test.docx`
5. Verify: non-empty DOCX with cover, TOC, at least one sourced image, Image Sources appendix

### Incremental Delivery

1. MVP (US1) → working `docforge render` command
2. US2 → `docforge analyse` (cheap addition, extends Analyser already built)
3. US3 → additional themes + i18n
4. US4 → `docforge doctor` + `docforge validate`
5. US5 → `Renderer` Python API
6. HTTP API → server mode for frontend
7. Additional image providers → Unsplash, Pexels

### Notes

- `[P]` tasks touch different files — safe to run in parallel
- Each phase delivers independently testable, demonstrable value
- Run `docforge doctor` before starting Phase 3 to confirm AI credentials
- Commit after each completed phase checkpoint
