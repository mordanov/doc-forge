# HTTP API Contract: DocForge

**Version**: 1.0
**Base URL**: `http://localhost:8000` (default; configurable)
**Auth**: Bearer JWT token obtained from `POST /auth/login`
**Content-Type**: `application/json` (except file uploads: `multipart/form-data`)

All responses are JSON. Errors use a consistent shape:
```json
{ "error": "<code>", "message": "<human-readable>", "suggestion": "<optional fix>" }
```

---

## Authentication

### POST /auth/login

Authenticate and obtain a session token.

**Request** (JSON):
```json
{ "username": "string", "password": "string" }
```

**Response 200**:
```json
{ "access_token": "string", "token_type": "bearer", "expires_in": 86400 }
```

**Errors**: `401 invalid_credentials`, `503 no_user_account` (init not run)

---

## Documents

### POST /documents/upload

Upload a `.docx` file. Returns a document id for use in subsequent calls.

**Request**: `multipart/form-data`, field `file` (`.docx` only, max 50 MB)

**Response 201**:
```json
{
  "document_id": "uuid",
  "filename": "guide.docx",
  "uploaded_at": "2026-07-26T10:00:00Z"
}
```

**Errors**: `400 invalid_format`, `413 file_too_large`

---

### POST /documents/{document_id}/analyse

Analyse a previously uploaded document. Returns semantic structure and statistics.

**Response 200**:
```json
{
  "document_id": "uuid",
  "title": "string",
  "language_detected": "en",
  "statistics": {
    "page_count_estimate": 42,
    "chapter_count": 8,
    "heading_count": 34,
    "table_count": 5,
    "placeholder_count": 12,
    "word_count": 18500
  },
  "chapters": [
    { "id": "uuid", "title": "string", "heading_level": 1, "element_count": 23 }
  ],
  "issues": [
    { "code": "orphan_heading", "message": "string", "location": "Chapter 3" }
  ]
}
```

**Errors**: `404 document_not_found`

---

## Jobs (Rendering)

### POST /jobs

Submit a new rendering job.

**Request**:
```json
{
  "document_id": "uuid",
  "config": {
    "template": "national_geographic",
    "language": "en",
    "ai": {
      "provider": "openai",
      "model": "gpt-4o",
      "creativity": 5
    },
    "images": {
      "enabled": true,
      "policy": "auto_search",
      "sources": ["wikimedia", "unsplash"],
      "density": "balanced"
    },
    "output": {
      "formats": ["docx"],
      "generate_cover": true,
      "generate_toc": true,
      "generate_page_numbers": true,
      "generate_headers_footers": true
    },
    "validation_level": "standard",
    "offline": false
  }
}
```

**Response 202**:
```json
{
  "job_id": "uuid",
  "status": "QUEUED",
  "stage": "UPLOADING",
  "progress": 0,
  "created_at": "2026-07-26T10:00:00Z"
}
```

**Errors**: `400 invalid_config`, `404 document_not_found`, `422 validation_error`

---

### GET /jobs/{job_id}

Poll the status of a rendering job.

**Response 200**:
```json
{
  "job_id": "uuid",
  "status": "RUNNING",
  "stage": "RENDERING",
  "progress": 65,
  "elapsed_seconds": 42.3,
  "warnings": ["Image placeholder p.12 could not be sourced — placeholder retained"],
  "error": null,
  "created_at": "2026-07-26T10:00:00Z",
  "started_at": "2026-07-26T10:00:01Z",
  "completed_at": null
}
```

When `status == "COMPLETED"`, also includes:
```json
{
  "output_urls": ["/jobs/{job_id}/download/docx"],
  "report": {
    "recovered_errors": [],
    "skipped_operations": [],
    "warnings": [],
    "fatal_failures": [],
    "suggested_actions": [],
    "image_attributions": [],
    "duration_seconds": 87.4
  }
}
```

**Errors**: `404 job_not_found`

---

### GET /jobs/{job_id}/download/{format}

Download a completed output file.

**Path params**: `format` ∈ `{docx}`

**Response 200**: Binary file stream (`Content-Disposition: attachment`)

**Errors**: `404 job_not_found`, `409 job_not_completed`, `400 format_not_available`

---

### DELETE /jobs/{job_id}

Cancel a queued or running job, or delete a completed/failed job record and its output files.

**Response 204**: No content

**Errors**: `404 job_not_found`

---

## Estimation

### POST /jobs/estimate

Pre-render estimate. Accepts the same payload as `POST /jobs`. Does not execute the render.

**Request**: Same as `POST /jobs`

**Response 200**:
```json
{
  "estimated_rendering_seconds": 120,
  "estimated_ai_tokens": 8400,
  "estimated_ai_requests": 12,
  "estimated_page_count": 45,
  "image_placeholder_count": 14,
  "validation_summary": {
    "warnings": [{ "code": "orphan_heading", "message": "string", "location": "Chapter 3" }],
    "errors": []
  },
  "licence_summary": {
    "providers_available": ["wikimedia", "unsplash"],
    "expected_licensed": 11,
    "expected_unlicensed": 3
  }
}
```

**Errors**: `400 invalid_config`, `404 document_not_found`

---

## Projects

### GET /projects

List all projects.

**Query params**: `page` (int, default 1), `per_page` (int, default 20), `sort` (`created_at|name`, default `created_at`), `order` (`asc|desc`, default `desc`)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "guide.docx",
      "template": "national_geographic",
      "language": "en",
      "ai_model": "gpt-4o",
      "status": "COMPLETED",
      "output_formats": ["docx"],
      "created_at": "2026-07-26T10:00:00Z",
      "completed_at": "2026-07-26T10:01:30Z"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20
}
```

---

### GET /projects/{project_id}

Get full project detail including config snapshot.

**Response 200**: Full Project object including `config_snapshot`.

**Errors**: `404 project_not_found`

---

### POST /projects/{project_id}/duplicate

Create a new job pre-populated with this project's configuration snapshot. Returns a new job object (status QUEUED) that can be modified before submission.

**Response 201**:
```json
{ "job_id": "uuid", "config": { /* copied snapshot */ } }
```

**Errors**: `404 project_not_found`

---

### DELETE /projects/{project_id}

Delete project record and associated output files. Does NOT delete the source input document.

**Response 204**: No content

**Errors**: `404 project_not_found`

---

## System

### GET /system/health

**Response 200**:
```json
{ "status": "ok", "version": "1.0.0", "initialized": true }
```

If `initialized: false`, auth endpoints still respond but all other endpoints return `503`.

### GET /system/themes

List available themes.

**Response 200**:
```json
{
  "themes": [
    { "id": "minimal", "name": "Minimal", "version": "1.0.0", "description": "string" }
  ]
}
```

### GET /system/providers

List configured and available AI and image providers.

**Response 200**:
```json
{
  "ai_providers": [{ "id": "openai", "available": true, "models": ["gpt-4o", "gpt-4o-mini"] }],
  "image_providers": [{ "id": "wikimedia", "available": true }, { "id": "unsplash", "available": false, "reason": "API key not configured" }]
}
```
