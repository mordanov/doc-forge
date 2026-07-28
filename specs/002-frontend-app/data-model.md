# Data Model: DocForge Frontend Application

**Feature**: `002-frontend-app`
**Date**: 2026-07-27

All types are TypeScript interfaces reflecting the **actual** backend API response shapes (not the contract documentation — see `research.md` §7 for divergence notes).

---

## Core API Types

### AuthToken

```typescript
interface AuthToken {
  access_token: string;
  token_type: 'bearer';
}
```

**Source**: `POST /auth/login`

---

### UploadedDocument

```typescript
interface UploadedDocument {
  id: string;          // UUID — use this as document_id in subsequent calls
  filename: string;
  size: number;        // bytes
}
```

**Source**: `POST /documents/upload`

---

### DocumentAnalysis

```typescript
interface DocumentAnalysis {
  document_id: string;
  statistics: {
    chapters: number;
    headings: number;
    tables: number;
    image_placeholders: number;
    words: number;
    estimated_pages: number;
  };
  issues: ValidationIssue[];
}

interface ValidationIssue {
  code: string;
  message: string;
  location: string;
}
```

**Source**: `POST /documents/{doc_id}/analyse`

---

### Job

```typescript
interface Job {
  id: string;
  project_id: string | null;
  status: JobStatus;
  stage: RenderStage;
  progress: number;           // 0–100
  elapsed_seconds: number;
  config_snapshot: string;    // JSON-encoded string
  input_filename: string;
  input_path: string;
  output_paths: string;       // JSON-encoded string — parse before use
  warnings: string;           // JSON-encoded string — parse before use
  error: string | null;
  created_at: string;         // ISO timestamp
  started_at: string | null;
  completed_at: string | null;
}

// Parsed form for use in components
interface ParsedJob extends Omit<Job, 'output_paths' | 'warnings'> {
  output_paths: string[];
  warnings: string[];
}

type JobStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

type RenderStage =
  | 'UPLOADING'
  | 'LOADING'
  | 'ANALYSING'
  | 'AI_PROCESSING'
  | 'IMAGE_SEARCH'
  | 'IMAGE_DOWNLOAD'
  | 'RENDERING'
  | 'VALIDATION'
  | 'EXPORT'
  | 'FINISHED';
```

**Source**: `GET /jobs/{job_id}`
**Note**: `output_paths` and `warnings` arrive as JSON-encoded strings and must be parsed by the API client layer.

---

### JobSubmitRequest

```typescript
interface JobSubmitRequest {
  document_id: string;
  template?: string;      // default: 'minimal'
  language?: string;      // default: 'en'
  ai_model?: string;      // default: 'gpt-4o'
  creativity?: number;    // default: 5, range 1–10
  config?: Record<string, unknown>;
}

interface JobSubmitResponse {
  job_id: string;
  status: 'QUEUED';
}
```

**Source**: `POST /jobs`

---

### JobEstimate

```typescript
interface JobEstimate {
  estimated_rendering_seconds: number;
  estimated_ai_tokens: number;
  estimated_ai_requests: number;
  estimated_page_count: number;
  image_placeholder_count: number;
  validation_summary: {
    warnings: string[];
    errors: string[];
  };
  licence_summary: {
    providers_available: string[];
    expected_licensed: number;
    expected_unlicensed: number;
  };
}
```

**Source**: `POST /jobs/estimate`

---

### Project

```typescript
interface Project {
  id: string;
  name: string;
  job_id: string;
  input_filename: string;
  config_snapshot: string;    // JSON-encoded string
  output_paths: string;       // JSON-encoded string — parse before use
  template: string;
  language: string;
  ai_model: string;
  status: string;
  created_at: string;
  completed_at: string | null;
}

// Parsed form for use in components
interface ParsedProject extends Omit<Project, 'output_paths' | 'config_snapshot'> {
  output_paths: string[];
  config_snapshot: Record<string, unknown>;
}
```

**Source**: `GET /projects`, `GET /projects/{id}`

---

### Theme

```typescript
interface Theme {
  id: string;
  version: string;
  author: string;
  supports_cover: boolean;
  supports_sidebars: boolean;
}
```

**Source**: `GET /system/themes`
**Note**: The backend does not return `name`, `description`, or preview images. Display names and descriptions must be maintained as frontend constants keyed by `id`.

---

### ProvidersStatus

```typescript
interface ProvidersStatus {
  ai: AIProviderStatus[];
  images: ImageProviderStatus[];
}

interface AIProviderStatus {
  id: string;
  available: boolean;
  reason?: string;       // present when unavailable
}

interface ImageProviderStatus {
  id: string;
  available: boolean;
  requires_key: boolean;
}
```

**Source**: `GET /system/providers`

---

### HealthCheck

```typescript
interface HealthCheck {
  status: 'ok';
  version: string;
}
```

**Source**: `GET /system/health`

---

### ApiError

```typescript
interface ApiError {
  detail: string;    // FastAPI default error shape
}
```

**Note**: All HTTP errors from the backend use this shape. Map `detail` to user-facing messages.

---

## Frontend-Only State Types

### WizardDraft

The in-progress state for the New Project wizard, held in Zustand `wizardStore` and persisted to `sessionStorage`.

```typescript
type WizardStep = 1 | 2 | 3 | 4 | 5;

interface WizardDraft {
  step: WizardStep;
  // Step 1 — Upload
  documentId: string | null;
  filename: string | null;
  analysis: DocumentAnalysis | null;
  // Step 2 — AI Configuration
  aiProvider: 'openai';
  aiModel: string;
  aiQuality: 'fast' | 'balanced' | 'maximum';
  creativity: number;            // 1–10
  // Step 3 — Publication Configuration
  presetId: string | null;
  template: string;
  outputFormats: OutputFormat[];
  language: string;
  imagePolicy: ImagePolicy;
  imageSources: string[];
  imageDensity: 'minimal' | 'balanced' | 'illustrated' | 'maximum';
  layoutDensity: 'compact' | 'balanced' | 'spacious';
  typography: string;
  colourPalette: string;
  customColour: string | null;
  sidebarStyle: string;
  coverPage: string;
  tableOfContents: string;
  headersFooters: string;
  validationLevel: 'fast' | 'standard' | 'strict';
  aiExplainability: 'off' | 'brief' | 'detailed';
  offlineMode: boolean;
  // Advanced
  promptVersion: string | null;
  themeVersion: string | null;
  parallelDownloads: number;
  retryCount: number;
  timeout: number;
  cacheLocation: string | null;
  cacheSize: number | null;
  maxAiRequests: number | null;
  // Step 4 — Estimate result
  estimate: JobEstimate | null;
  // Step 5 — Active job
  activeJobId: string | null;
}

type OutputFormat = 'docx' | 'pdf' | 'html' | 'markdown' | 'epub';
type ImagePolicy = 'auto' | 'placeholders_only' | 'preserve' | 'disable';
```

---

### Preset

Built-in configuration bundles maintained as frontend constants.

```typescript
interface Preset {
  id: string;
  name: string;
  description: string;
  config: Partial<WizardDraft>;  // values this preset sets
}
```

Built-in preset IDs: `travel-guide`, `book`, `magazine`, `academic-paper`, `annual-report`, `corporate-report`, `newsletter`.

---

### AppSettings

Persisted to `localStorage`.

```typescript
interface AppSettings {
  theme: 'light' | 'dark';
  defaultLanguage: string;
  defaultOutputFormat: OutputFormat;
  defaultTemplate: string;
  openAiApiKey: string | null;   // stored obfuscated; never logged
}
```

---

## State Transitions

### Job Status Flow

```
QUEUED → RUNNING → COMPLETED
                 ↘ FAILED
       → CANCELLED  (before RUNNING only)
```

### Wizard Step Flow

```
1 (Upload) → 2 (AI Config) → 3 (Publication Config) → 4 (Preview/Estimate) → 5 (Rendering) → Done
```

Steps 1–3 allow backward navigation. Steps 4–5 are forward-only once a job is submitted.
