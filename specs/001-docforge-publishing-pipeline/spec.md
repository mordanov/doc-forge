# Feature Specification: DocForge Automated Publishing Pipeline

**Feature Branch**: `001-docforge-publishing-pipeline`
**Created**: 2026-07-26
**Status**: Draft
**Input**: User description from `documentation/initial-specification.md`

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Document Rendering (Priority: P1)

A user has a Microsoft Word document (`.docx`) containing travel guide content with text, tables, and image placeholders.
They want to produce a publication-quality Word document with professional typography,
styled tables, sourced and licensed photographs, a cover page, table of contents, headers,
footers, and an image attribution appendix — without manually formatting anything.

**Why this priority**: This is the core value of DocForge. Everything else is secondary to
the ability to load a DOCX, apply a theme, source legal images, and write a polished output file.

**Independent Test**: Can be fully tested by running `docforge render input.docx output.docx`
and verifying the output DOCX contains styled content, sourced images with captions, a cover,
a TOC, and an Image Sources appendix — all without modifying the source document.

**Acceptance Scenarios**:

1. **Given** a valid `.docx` with text, tables, and image placeholders, **When** the user runs
   `docforge render input.docx output.docx --template national_geographic --language en`,
   **Then** the output DOCX contains a cover page, TOC, styled body, sourced images with captions,
   headers, footers, page numbers, and an Image Sources appendix.

2. **Given** a document with image placeholders where no licensed images can be found,
   **When** rendering completes, **Then** placeholders remain visible, a warning is logged,
   and rendering does not terminate; the rest of the document is fully rendered.

3. **Given** identical input, configuration, template, and cached assets across two separate
   rendering runs, **When** both runs complete, **Then** both output documents are semantically
   equivalent (same structure, styles, content, and image assignments).

---

### User Story 2 — Document Analysis (Priority: P2)

A user wants to inspect a document before rendering — understanding its structure, detected
placeholders, and potential issues — without making any modifications.

**Why this priority**: Enables informed rendering decisions and surfaces problems early,
before committing to a full render cycle.

**Independent Test**: Can be fully tested by running `docforge analyse input.docx` and
verifying a structured report is produced with chapter list, placeholder inventory, and
detected issues — with zero changes to the source file.

**Acceptance Scenarios**:

1. **Given** a `.docx` file, **When** the user runs `docforge analyse input.docx`,
   **Then** a report is produced listing chapters, headings, image placeholders, tables,
   detected issues, and document statistics; the source file remains unmodified.

2. **Given** a document with structural problems (orphan headings, missing captions),
   **When** the analysis completes, **Then** the report explicitly lists each issue with
   actionable guidance for resolution.

---

### User Story 3 — Configuration & Theme Selection (Priority: P2)

A user wants to configure rendering behaviour — selecting a theme, language, AI provider,
image providers, and output options — through a YAML configuration file or CLI flags.

**Why this priority**: Without flexible configuration, every user is locked to defaults.
Configuration unlocks professional workflows and automation.

**Independent Test**: Can be fully tested by providing a `docforge.yaml` config file with
non-default settings and verifying rendered output reflects those settings without touching source code.

**Acceptance Scenarios**:

1. **Given** a YAML config file specifying `template: lonely_planet` and `language: ru`,
   **When** the user renders a document using that config, **Then** the output uses the
   Lonely Planet visual theme and all auto-generated text (TOC label, captions, appendix heading)
   is in Russian.

2. **Given** an invalid configuration file (unknown template name, invalid provider key),
   **When** the user attempts to render, **Then** execution stops before processing begins,
   and a clear error message identifies the invalid field, expected value, and suggested correction.

3. **Given** both a config file and CLI flags providing the same setting,
   **When** rendering runs, **Then** the CLI flag value takes precedence over the config file value.

---

### User Story 4 — Validation & Doctor (Priority: P3)

A user wants to verify their environment is correctly set up, and validate their configuration,
templates, and document before investing in a full rendering run.

**Why this priority**: Reduces wasted rendering time and helps first-time users self-diagnose
setup issues independently.

**Independent Test**: Can be fully tested by running `docforge validate` and `docforge doctor`
against a known-good and known-bad environment, verifying pass/fail outcomes and actionable messages.

**Acceptance Scenarios**:

1. **Given** a correctly configured environment, **When** the user runs `docforge doctor`,
   **Then** all checks (Python version, credentials, internet, fonts, image libraries) pass
   with clear output.

2. **Given** a configuration referencing a non-existent theme, **When** the user runs
   `docforge validate`, **Then** the command reports the invalid theme, the expected location,
   and a suggested fix; exit code is non-zero.

---

### User Story 5 — Python API Integration (Priority: P3)

A developer wants to embed DocForge rendering into their own Python application or CI pipeline
using a programmatic API rather than the CLI.

**Why this priority**: Enables integration into automation workflows, CI/CD, and custom tooling
without subprocess calls.

**Independent Test**: Can be fully tested by calling `Renderer().render(input_path, output_path)`
in a Python script and verifying it produces the same output as the equivalent CLI invocation.

**Acceptance Scenarios**:

1. **Given** a Python script importing `from docforge import Renderer`, **When** the script
   calls `Renderer().template("minimal").language("en").render("in.docx", "out.docx")`,
   **Then** the output file is produced with the Minimal theme and the call is fully equivalent
   to the CLI counterpart.

2. **Given** an async execution context, **When** the developer uses the async render API,
   **Then** AI requests and image downloads are performed concurrently without blocking the
   event loop.

---

### Edge Cases

- What happens when the input `.docx` is password-protected or corrupted?
  → Fatal error with clear diagnostic; no partial output written.
- What happens when all configured image providers are unavailable (network offline)?
  → Offline mode activates; cached images are used where available; placeholders remain for uncached positions; rendering continues.
- What happens when an image download succeeds but licence metadata is unavailable?
  → Image is NOT embedded; placeholder remains; a warning is logged identifying the image URL.
- What happens when an AI provider returns a response that fails schema validation?
  → Automatic retry (configurable count); if retries exhausted, fallback to default layout decisions; warning is logged.
- What happens when the output file path already exists?
  → Overwritten by default; configurable to prompt or fail.
- What happens when a theme declares inheritance from a non-existent base theme?
  → Theme validation fails at startup with actionable error before rendering begins.
- What happens when the HTTP server starts but `docforge init` has not been run?
  → Server refuses to start, prints a clear error message directing the user to run `docforge init`.
- What happens when `DOCFORGE_USERNAME` or `DOCFORGE_PASSWORD` is missing from `.env` during init?
  → `docforge init` exits with a clear error identifying the missing variable before creating any files.

---

## Requirements *(mandatory)*

### Functional Requirements

**Document Handling**

- **FR-001**: The system MUST load `.docx` files and preserve all original textual content
  (paragraphs, lists, tables, hyperlinks, bookmarks, references, page order) unchanged.
- **FR-002**: The system MUST NEVER modify the source document; all output is written to a
  separate output path.
- **FR-003**: The system MUST build an internal semantic document model
  (Document → Section → Chapter → Paragraph → Heading → Table → Row → Cell →
  ImagePlaceholder → Image → Caption → Sidebar → PageBreak → Header → Footer → Appendix)
  before rendering.

**Rendering & Output**

- **FR-004**: The system MUST produce a valid, editable `.docx` output compatible with
  Microsoft Word and LibreOffice.
- **FR-005**: The system MUST apply configurable visual themes to typography, colours,
  spacing, borders, and decorative elements.
- **FR-006**: The system MUST optionally generate: cover page, table of contents, page numbers,
  headers, and footers — each independently togglable via configuration.
- **FR-007**: Rendering MUST be deterministic: identical input + configuration + template +
  cached assets MUST produce semantically equivalent output on every run.
- **FR-008**: The rendering engine MUST validate layout before export, checking heading
  hierarchy, page breaks, orphan headings, widow paragraphs, oversized images, overlapping
  content, caption placement, table overflow, and section consistency.

**Image Pipeline**

- **FR-009**: The system MUST replace image placeholders with legally reusable photographs
  (Public Domain, CC0, CC BY, CC BY-SA) sourced from configured providers.
- **FR-010**: Every embedded image MUST include a caption, source attribution, licence
  identifier, and provenance metadata.
- **FR-011**: The system MUST generate a mandatory "Image Sources" appendix listing for each
  image: page number, figure identifier, image title, photographer, source, URL, licence,
  and retrieval date.
- **FR-012**: Images whose licence cannot be verified MUST NOT be embedded automatically;
  the placeholder MUST remain and a warning MUST be logged.
- **FR-013**: Downloaded images MUST be cached and reused across runs using a cache key
  incorporating source URL, checksum, licence, requested dimensions, and optimisation parameters.
- **FR-014**: The image download manager MUST validate MIME type, file extension, integrity,
  and enforce maximum size limits; failed downloads MUST NOT terminate rendering.

**AI Decision Engine**

- **FR-015**: The AI engine MUST produce structured JSON rendering instructions only;
  it MUST NEVER edit documents directly.
- **FR-016**: The system MUST support an AI provider abstraction layer; adding a new provider
  MUST require only a new adapter with no business logic changes.
- **FR-017**: Prompts MUST be stored as versioned configuration files separate from source code;
  each prompt MUST include a unique identifier, semantic version, description, supported providers,
  expected response schema, and validation rules.
- **FR-018**: All AI responses MUST conform to a predefined JSON schema; invalid responses
  MUST be rejected and retried; rendering MUST fall back to default layout decisions if retries
  are exhausted.
- **FR-019**: The AI engine MUST cache responses and reuse them for identical chapter context
  to minimise token usage.
- **FR-019a**: The AI subsystem configuration MUST accept a `model` parameter (string,
  provider-specific model identifier) and a `creativity` parameter (integer 1–10, where 1 =
  conservative/deterministic and 10 = highly creative editorial design); each provider adapter
  MUST map these to its own sampling/temperature settings.
- **FR-019b**: The HTTP API job submission payload MUST include `ai.model` and `ai.creativity`
  as explicit fields; both MUST be validated against the selected provider's supported models
  and the 1–10 range respectively before job execution begins.

**Configuration System**

- **FR-020**: The system MUST load configuration from: CLI arguments (highest precedence) >
  environment variables > project YAML/TOML config file > built-in defaults.
- **FR-021**: Configuration MUST be validated before execution begins; invalid configuration
  MUST stop execution with a message identifying parameter name, expected type, actual value,
  and suggested correction.
- **FR-022**: The system MUST support named configuration profiles (development, production,
  ci, offline, travel-guide, book, report) with profile inheritance.

**CLI**

- **FR-023**: The system MUST provide a `docforge render` command as the primary interface.
- **FR-023a**: The system MUST provide a `docforge init` command that: creates the local
  project structure, reads `DOCFORGE_USERNAME` and `DOCFORGE_PASSWORD` from `.env`, creates
  and persists a hashed user account, and confirms readiness. Subsequent `init` invocations
  MUST be idempotent (re-running does not overwrite an existing account unless `--force` is
  passed).
- **FR-024**: The system MUST provide: `analyse`, `validate`, `themes`, `cache`, `prompts`,
  `providers`, `doctor`, `version`, `config`, `export`, `images`, `clean` sub-commands.
- **FR-025**: The `doctor` command MUST check Python version, dependencies, API credentials,
  internet connectivity, cache availability, fonts, and image libraries.
- **FR-026**: CLI MUST remain stable across minor releases; machine-readable output (JSON)
  MUST be available for all commands that produce structured results.

**Python API**

- **FR-027**: The Python API MUST be a first-class interface; the CLI MUST be implemented
  using the public Python API.
- **FR-028**: The API MUST support both synchronous and asynchronous execution; long-running
  operations (AI requests, image downloads) MUST be async-capable.
- **FR-029**: Public API interfaces MUST carry type annotations; breaking changes MUST
  increment the major semantic version.

**Internationalisation**

- **FR-030**: The system MUST support at minimum: Russian, English, Spanish, German, French.
- **FR-031**: All auto-generated text (TOC label, figure captions, appendix heading, page labels)
  MUST be localised to the document's configured language.
- **FR-032**: The renderer MUST apply language-specific typography rules (quotation marks,
  punctuation spacing, date formats, list formatting).

**Logging & Observability**

- **FR-033**: Every execution MUST produce a structured log capturing: document loading,
  template selection, AI provider, prompt version, rendering decisions, image downloads,
  licence verification, caching activity, warnings, and failures.
- **FR-034**: JSON-format logging MUST be supported; verbosity level MUST be configurable
  (TRACE / DEBUG / INFO / WARNING / ERROR / CRITICAL).
- **FR-035**: Long-running operations MUST report incremental progress to the user.

**Plugin Architecture**

- **FR-036**: The system MUST support independently versioned plugins for: AI providers,
  image providers, themes, exporters, document analysers, post-processors, metadata providers,
  and validators.
- **FR-037**: Plugins MUST communicate only through the public extension API; direct access
  to internal application state is forbidden.

**Authentication** *(added to secure the HTTP API — see Clarifications)*

- **FR-047**: The HTTP server MUST require authentication on all endpoints. The authentication
  mechanism is username/password, verified against credentials stored in a local user account
  created during initialisation.
- **FR-048**: Credentials (username and password) MUST be configured exclusively through a
  `.env` file; they MUST NEVER be hardcoded, committed to version control, or appear in logs.
- **FR-049**: A `docforge init` command (or equivalent initialisation step) MUST create the
  local user account from the `.env` credentials before the HTTP server can accept requests;
  running the server without a provisioned account MUST produce a clear error directing the
  user to run `docforge init`.
- **FR-050**: Passwords MUST be stored as a salted hash; plain-text passwords MUST NEVER be
  persisted to disk.
- **FR-051**: The HTTP API MUST issue a session token on successful login; subsequent requests
  MUST present the token in the `Authorization` header; token lifetime and invalidation MUST
  be configurable.

**HTTP API** *(added to support the planned frontend — see Clarifications)*

- **FR-038**: The system MUST expose a minimal HTTP API providing at least the following
  endpoints: document upload, document analysis (returns semantic structure and statistics),
  rendering job submission (accepts configuration payload), job status polling (returns stage,
  progress, elapsed time, warnings), and output file download.
- **FR-039**: The HTTP API MUST be implemented as a thin adapter layer on top of the public
  Python API; no rendering logic MUST reside in the HTTP layer.
- **FR-040**: Job status responses MUST include a machine-readable stage identifier matching
  the rendering pipeline stages (Uploading, Analysing, AI Processing, Searching Images,
  Downloading Images, Rendering, Validation, Export, Finished) and a structured warnings list.
- **FR-041**: The HTTP API MUST support long-running jobs asynchronously; clients poll for
  status rather than holding a blocking connection.
- **FR-042**: The HTTP API MUST return structured JSON responses with consistent error shapes
  (error code, message, suggested action) for all failure conditions.
- **FR-042a**: The HTTP API MUST expose a pre-render estimation endpoint that accepts a full
  job configuration payload and returns without executing the render: estimated rendering time,
  estimated AI token cost, estimated AI request count, estimated output page count, image
  placeholder count, a validation summary (warnings and errors), and a licence pre-check
  summary. Estimates are best-effort; actual values may differ.

**Project Store** *(local persistence — see Clarifications)*

- **FR-043**: The system MUST maintain a local project store recording for each job: job id,
  input filename, configuration snapshot, output file paths, rendering status, and timestamps
  (created, started, completed).
- **FR-044**: The HTTP API MUST expose project list, project detail, project duplication,
  output download, and project deletion endpoints backed by the local project store.
- **FR-045**: The project store MUST use a filesystem-based backend in Version 1.0; the
  architecture MUST permit swapping to a remote backend (database, cloud storage) without
  changing the HTTP API contract.
- **FR-046**: Project deletion MUST remove the associated output files and job record;
  the input source document MUST NOT be deleted.

### Key Entities

- **Document**: Top-level container; carries language, title, source path, metadata.
- **SemanticModel**: Structured tree (Sections → Chapters → Paragraphs, Tables, Images, etc.)
  produced by the analyser; consumed by the rendering engine.
- **RenderingDecision**: Structured JSON produced by the AI engine specifying layout choices
  (photo layout, sidebar usage, typography adjustments, table style, etc.).
- **Theme**: Declarative YAML definition of visual identity (colours, typography, spacing,
  borders, icons, decorations); carries a manifest with id, version, inheritance chain.
- **ImageCandidate**: A photo candidate from a provider with source URL, licence, resolution,
  orientation, and relevance score.
- **CachedAsset**: A locally stored image keyed by URL + checksum + dimensions + licence;
  includes retrieval date and provenance metadata.
- **Prompt**: Versioned configuration artefact with unique id, version, description, supported
  providers, context requirements, and expected response schema.
- **PluginManifest**: YAML descriptor for any plugin; includes id, name, version, api_version,
  entrypoint, and capabilities list.
- **RenderingReport**: End-of-run summary of recovered errors, skipped operations, warnings,
  fatal failures, and suggested actions.
- **RenderingJob**: Server-side representation of an async render request; carries job id,
  current stage, progress percentage, elapsed time, warnings list, and output file reference
  when complete. Used by the HTTP API.
- **Project**: Persisted record in the local project store; carries job id, input filename,
  configuration snapshot, output file paths, rendering status, and created/started/completed
  timestamps. Supports list, detail, duplicate, download, and delete operations via the HTTP API.
- **UserAccount**: Local authentication record created by `docforge init`; stores username
  and salted password hash; sourced from `.env` variables `DOCFORGE_USERNAME` and
  `DOCFORGE_PASSWORD`; never stored in plain text.
- **RenderEstimate**: Best-effort pre-render projection returned by the estimation endpoint;
  includes estimated rendering time, AI token cost, AI request count, output page count,
  image placeholder count, validation summary, and licence pre-check summary.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user with no prior DocForge experience can install, configure, and successfully
  render a publication from the official documentation in under 30 minutes.
- **SC-002**: A 100-page document completes full rendering (including image search and AI
  decisions) in under 10 minutes on contemporary desktop hardware using a warm cache.
- **SC-003**: Repeated rendering of identical input with identical configuration produces
  semantically equivalent output on 100% of runs (zero non-deterministic variation).
- **SC-004**: At least 90% of image placeholders in a well-tagged document are replaced with
  a legally sourced, licence-verified photograph in a standard rendering run.
- **SC-005**: No manual formatting corrections are required after a successful rendering run
  on a document that conforms to the input conventions.
- **SC-006**: A new AI provider or image provider can be integrated by adding a single adapter
  module — no changes to existing business logic files.
- **SC-007**: A single non-fatal failure (missing image, AI timeout) does not prevent the
  remaining document from being fully rendered and exported.
- **SC-008**: Unit test coverage of business logic reaches 100%; overall project coverage
  reaches 95%+; all CI quality gates (linting, static analysis, golden tests) pass on every
  release.

---

## Clarifications

### Session 2026-07-26

- Q: Should a minimal HTTP API be included in Version 1.0 to support the planned frontend? → A: Yes — include a minimal HTTP API covering document upload, analysis, rendering job submission, status polling, and output download.
- Q: Should project persistence be included in Version 1.0? → A: Yes — include a lightweight local project store (filesystem-based) recording job id, input filename, config snapshot, output paths, status, and timestamps; queryable via the HTTP API.
- Q: Should AI model selection and a creativity/temperature parameter be first-class configuration options? → A: Yes — add model selection and creativity (integer 1–10) as explicit parameters in the AI subsystem configuration contract and HTTP API job submission payload.
- Q: Should the HTTP API include a pre-render estimation endpoint? → A: Yes — add an estimation endpoint that accepts job configuration and returns estimated rendering time, AI token cost, request count, page count, image opportunities, and a warnings/validation summary without executing the render.
- Q: Should the HTTP API require authentication? → A: Yes — simple username/password auth; credentials configured via `.env` file; user account created automatically on first `docforge init` run; all API endpoints require authentication.

---

## Assumptions

- Input documents are well-formed `.docx` files produced by Microsoft Word or a compatible application.
- Image placeholders are identified by a consistent convention (e.g., paragraph text or
  bookmark naming) that the Document Analyser can detect deterministically.
- The user provides valid API credentials for at least one AI provider and at least one
  image provider; the `doctor` command surfaces missing credentials before any rendering attempt.
- The target deployment environments (Linux, macOS, Windows) have Python 3.11+ available.
- Offline mode relies on a previously populated local cache; first-run offline rendering
  is not a supported scenario for image sourcing.
- PDF, HTML, EPUB, and Markdown export are out of scope for Version 1.0; the architecture
  accommodates them as future exporters.
- Desktop GUI, collaborative editing, OCR, PowerPoint/Excel editing, and AI text generation
  are explicitly out of scope for Version 1.x.
- Themes are distributed as part of the DocForge package or installed as plugins; custom
  theme creation by end users is supported but not guided by a wizard in Version 1.0.
- The "Image Sources" appendix is always generated when at least one image is embedded;
  it cannot be disabled by configuration in Version 1.0.
- Authentication credentials are single-user only in Version 1.0; multi-user support is
  explicitly out of scope.
- The `.env` file is the only supported credential source; secret managers and external
  identity providers are out of scope for Version 1.0.
