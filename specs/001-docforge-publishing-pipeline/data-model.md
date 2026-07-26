# Data Model: DocForge Automated Publishing Pipeline

**Date**: 2026-07-26

---

## Domain Entities

### Document (in-memory, not persisted)

Loaded from source `.docx` by the Document Loader. Never modified.

```
Document
  id            : str          # UUID, assigned at load time
  source_path   : Path         # Absolute path to input .docx
  title         : str          # Extracted from document properties or first heading
  language      : str          # ISO 639-1 code, e.g. "en", "ru"
  metadata      : DocumentMeta # Author, keywords, created, modified
  sections      : list[Section]
```

```
DocumentMeta
  author        : str | None
  subject       : str | None
  keywords      : list[str]
  created       : datetime | None
  modified      : datetime | None
```

---

### SemanticModel (in-memory, not persisted)

Produced by the Document Analyser from a Document. Consumed by the AI Engine and Rendering Engine.

```
SemanticModel
  document_id   : str
  chapters      : list[Chapter]
  statistics    : DocumentStatistics
```

```
Chapter
  id            : str
  title         : str
  heading_level : int           # 1–6
  elements      : list[Element] # ordered
```

```
Element  (discriminated union)
  Paragraph     : { text, style, runs: list[Run] }
  Heading       : { text, level: int }
  Table         : { rows: list[Row] }
  ImagePlaceholder : { placeholder_text: str, context_hint: str }
  Image         : { asset: CachedAsset, caption: str, placement: Placement }
  Caption       : { text: str, figure_id: str }
  Sidebar       : { style: SidebarStyle, content: list[Paragraph] }
  PageBreak     : {}
  Header        : { text: str, odd: bool }
  Footer        : { text: str, odd: bool }
  Appendix      : { title: str, entries: list[ImageAttribution] }
```

```
Row     : { cells: list[Cell] }
Cell    : { content: list[Paragraph] }
Run     : { text: str, bold: bool, italic: bool, underline: bool, style: str | None }
Placement : INLINE | FLOAT_LEFT | FLOAT_RIGHT | FULL_WIDTH
SidebarStyle : NONE | MINIMAL | EDITORIAL | MAGAZINE
```

```
DocumentStatistics
  page_count_estimate : int
  chapter_count       : int
  heading_count       : int
  table_count         : int
  placeholder_count   : int
  word_count          : int
```

---

### RenderingDecision (in-memory, not persisted)

Structured JSON produced by the AI Engine for each chapter. Validated against a Pydantic schema.

```
RenderingDecision
  chapter_id      : str
  chapter_style   : ChapterStyle     # STANDARD | FEATURE | OPENER
  photo_layout    : PhotoLayout      # NONE | INLINE | TWO_COLUMN | FULL_WIDTH | MAGAZINE
  sidebar         : SidebarDecision
  table_style     : str              # theme-defined table style name
  typography_variant : str           # CONSERVATIVE | EDITORIAL | MAGAZINE | LUXURY
  heading_colour  : str | None       # optional hex override
  pull_quote      : bool
  callout         : bool
  page_balance    : PageBalance      # TIGHT | BALANCED | SPACIOUS

SidebarDecision
  enabled : bool
  type    : SidebarStyle

ChapterStyle   : STANDARD | FEATURE | OPENER
PhotoLayout    : NONE | INLINE | TWO_COLUMN | FULL_WIDTH | MAGAZINE
PageBalance    : TIGHT | BALANCED | SPACIOUS
```

---

### RenderingJob (persisted in SQLite: `jobs` table)

Created when a render request is received by the HTTP API.

```
RenderingJob
  id              : str          # UUID
  project_id      : str | None   # FK → Project.id (set when job completes successfully)
  status          : JobStatus
  stage           : RenderStage
  progress        : int          # 0–100
  elapsed_seconds : float
  config_snapshot : dict         # JSON-serialised configuration at submission time
  input_filename  : str
  input_path      : Path         # Absolute path to uploaded .docx
  output_paths    : list[Path]   # Populated on completion
  warnings        : list[str]
  error           : str | None
  created_at      : datetime
  started_at      : datetime | None
  completed_at    : datetime | None

JobStatus : QUEUED | RUNNING | COMPLETED | FAILED | CANCELLED
RenderStage : UPLOADING | ANALYSING | AI_PROCESSING | SEARCHING_IMAGES |
              DOWNLOADING_IMAGES | RENDERING | VALIDATION | EXPORT | FINISHED
```

---

### Project (persisted in SQLite: `projects` table)

Created from a completed RenderingJob. Supports list/detail/duplicate/download/delete.

```
Project
  id              : str          # UUID
  name            : str          # Derived from input filename; editable
  job_id          : str          # FK → RenderingJob.id
  input_filename  : str
  config_snapshot : dict         # JSON; used for duplication
  output_paths    : list[Path]
  template        : str          # Theme name used
  language        : str          # ISO 639-1
  ai_model        : str          # e.g. "gpt-4o"
  status          : JobStatus    # Mirrors job status at snapshot time
  created_at      : datetime
  completed_at    : datetime | None
```

---

### UserAccount (persisted in SQLite: `user_accounts` table)

Single row in v1. Created by `docforge init`.

```
UserAccount
  id              : int          # Primary key, always 1 in v1
  username        : str          # From DOCFORGE_USERNAME env var
  password_hash   : str          # bcrypt hash (work factor 12)
  created_at      : datetime
```

---

### RenderEstimate (in-memory, not persisted)

Returned by the estimation endpoint. Best-effort projections.

```
RenderEstimate
  estimated_rendering_seconds  : int
  estimated_ai_tokens          : int
  estimated_ai_requests        : int
  estimated_page_count         : int
  image_placeholder_count      : int
  validation_summary           : ValidationSummary
  licence_summary              : LicenceSummary

ValidationSummary
  warnings : list[ValidationIssue]
  errors   : list[ValidationIssue]

LicenceSummary
  providers_available : list[str]
  expected_licensed   : int
  expected_unlicensed : int   # will remain as placeholders

ValidationIssue
  code    : str
  message : str
  location: str | None   # e.g. "Chapter 3, Heading 2"
```

---

### Theme (loaded from YAML, not persisted)

```
Theme
  id          : str
  version     : str          # Semver
  author      : str
  inherits    : str | None   # Parent theme id
  manifest    : ThemeManifest
  palette     : ColourPalette
  typography  : TypographyConfig
  spacing     : SpacingConfig
  table_style : TableStyleConfig
  sidebar     : SidebarStyleConfig
  cover       : CoverConfig
  icons       : dict[str, Path]
  decorations : list[DecorationConfig]

ThemeManifest
  supports_cover    : bool
  supports_sidebars : bool
  supports_icons    : bool
```

---

### Prompt (loaded from YAML, not persisted)

```
Prompt
  id               : str       # Unique identifier, e.g. "editorial_v1"
  version          : str       # Semver
  description      : str
  providers        : list[str] # Supported AI providers
  template         : str       # Jinja2 template string
  response_schema  : dict      # JSON Schema for expected AI response
  context_fields   : list[str] # Required context keys
```

---

### ImageCandidate (in-memory, not persisted)

```
ImageCandidate
  provider    : str
  url         : str
  title       : str
  author      : str | None
  licence     : LicenceType
  width       : int
  height      : int
  orientation : Orientation    # LANDSCAPE | PORTRAIT | SQUARE
  relevance   : float          # 0.0–1.0 (provider-reported or rank-derived)
  source_page : str | None     # URL of the source page for attribution

LicenceType : PUBLIC_DOMAIN | CC0 | CC_BY | CC_BY_SA | UNSUPPORTED | UNKNOWN
Orientation : LANDSCAPE | PORTRAIT | SQUARE
```

---

### CachedAsset (persisted on filesystem as file + JSON sidecar)

```
CachedAsset
  cache_key     : str     # SHA-256 of (url + checksum + dimensions + licence)
  source_url    : str
  local_path    : Path
  licence       : LicenceType
  author        : str | None
  title         : str | None
  source_page   : str | None
  width         : int
  height        : int
  file_size     : int
  retrieved_at  : datetime
  checksum      : str     # SHA-256 of file contents
```

---

### PluginManifest (loaded from YAML, not persisted)

```
PluginManifest
  id           : str
  name         : str
  version      : str       # Semver
  api_version  : int       # Plugin API contract version
  entrypoint   : str       # Python module path
  capabilities : list[str] # e.g. ["image_search", "image_download"]
  license      : str
  author       : str
```

---

### RenderingReport (in-memory, included in job completion payload)

```
RenderingReport
  job_id              : str
  recovered_errors    : list[str]
  skipped_operations  : list[str]
  warnings            : list[str]
  fatal_failures      : list[str]
  suggested_actions   : list[str]
  image_attributions  : list[ImageAttribution]
  duration_seconds    : float

ImageAttribution
  figure_id     : str
  page_number   : int | None
  title         : str
  photographer  : str | None
  source        : str
  url           : str
  licence       : LicenceType
  retrieved_at  : datetime
```

---

## SQLite Schema

```sql
CREATE TABLE user_accounts (
  id            INTEGER PRIMARY KEY,   -- always 1 in v1
  username      TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at    TEXT NOT NULL          -- ISO 8601
);

CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  project_id      TEXT,
  status          TEXT NOT NULL,       -- JobStatus enum value
  stage           TEXT NOT NULL,       -- RenderStage enum value
  progress        INTEGER NOT NULL DEFAULT 0,
  elapsed_seconds REAL NOT NULL DEFAULT 0,
  config_snapshot TEXT NOT NULL,       -- JSON
  input_filename  TEXT NOT NULL,
  input_path      TEXT NOT NULL,
  output_paths    TEXT NOT NULL DEFAULT '[]',  -- JSON array
  warnings        TEXT NOT NULL DEFAULT '[]',  -- JSON array
  error           TEXT,
  created_at      TEXT NOT NULL,
  started_at      TEXT,
  completed_at    TEXT
);

CREATE TABLE projects (
  id              TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  job_id          TEXT NOT NULL,
  input_filename  TEXT NOT NULL,
  config_snapshot TEXT NOT NULL,       -- JSON
  output_paths    TEXT NOT NULL,       -- JSON array
  template        TEXT NOT NULL,
  language        TEXT NOT NULL,
  ai_model        TEXT NOT NULL,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  completed_at    TEXT,
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

---

## State Transitions

### RenderingJob lifecycle

```
QUEUED → RUNNING → COMPLETED
               ↘ FAILED
       ← CANCELLED (from QUEUED or RUNNING)
```

### RenderStage progression (within RUNNING status)

```
UPLOADING → ANALYSING → AI_PROCESSING → SEARCHING_IMAGES →
DOWNLOADING_IMAGES → RENDERING → VALIDATION → EXPORT → FINISHED
```

Any stage failure transitions job status to FAILED; the stage field retains the failing stage.
