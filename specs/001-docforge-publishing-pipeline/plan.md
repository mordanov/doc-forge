# Implementation Plan: DocForge Automated Publishing Pipeline

**Branch**: `001-docforge-publishing-pipeline` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-docforge-publishing-pipeline/spec.md`

## Summary

DocForge is a Python CLI tool, library, and local HTTP service that transforms `.docx`
documents into publication-quality Word documents using deterministic rendering and AI-assisted
editorial decisions. The system sources legally-licensed photographs, applies configurable
visual themes, generates covers, TOCs, headers/footers, and image attribution appendices.

Core technical approach:
- **python-docx** for DOCX read/write
- **FastAPI** for the HTTP API layer (async, OpenAPI-documented)
- **OpenAI** as the initial AI provider via an abstraction layer
- **SQLite** (via `sqlite3` stdlib) for the local project store
- **bcrypt** for password hashing; JWT tokens for session auth
- **pytest** test pyramid: unit → integration → rendering → golden → e2e
- **Ruff + MyPy + Bandit** for static analysis

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, python-docx, Pydantic v2, httpx, Pillow, bcrypt,
  python-jose (JWT), Ruff, MyPy, Bandit, pytest, pytest-asyncio, structlog
**Storage**: Local filesystem (image cache, output files); SQLite (project store, user account)
**Testing**: pytest with pytest-asyncio; golden document tests; visual snapshot tests
**Target Platform**: Linux, macOS, Windows (Python 3.11+, cross-platform)
**Project Type**: Python library + CLI tool + local HTTP service
**Performance Goals**: 100-page document renders in under 10 minutes (warm cache);
  image downloads parallelised; AI requests cached per chapter context
**Constraints**: Deterministic rendering; offline-capable (cached assets); single-user auth
  via `.env`; secrets never in logs; all AI responses schema-validated
**Scale/Scope**: Single-user local deployment in Version 1.0; architecture supports
  multi-user remote deployment in future versions

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Software First — AI advisory only, deterministic execution | ✅ PASS | AI engine produces JSON instructions only; Rendering Engine executes. No AI direct document access. |
| II. Deterministic Rendering — identical inputs → identical output | ✅ PASS | FR-007 mandates determinism; golden document tests enforce it; randomness forbidden in layout. |
| III. Human Ownership — presentation only, no content changes | ✅ PASS | FR-001/FR-002 prohibit content modification; DocForge never rewrites author text. |
| IV. Modular Independence — single responsibility, explicit interfaces | ✅ PASS | Layered architecture (CLI → Application → Domain → Infrastructure); plugin interfaces; no circular deps. |
| V. Legal Compliance — licence-verified images only, Image Sources mandatory | ✅ PASS | FR-009/FR-012 enforce licence gating; FR-011 mandates Image Sources appendix as quality gate. |
| VI. Quality Gates & DoD — automated tests, visual validation, CI | ✅ PASS | SC-008 sets 95%/100% coverage targets; rendering tests required; CI gates defined. |
| VII. Security — no code execution, validated assets, secrets in env only | ✅ PASS | FR-047–051 add single-user auth; credentials via `.env`; hashed storage; no secrets in logs. |
| VIII. Configuration Over Code — YAML/TOML config, versioned prompts and themes | ✅ PASS | FR-020–022 define configuration precedence; FR-017 mandates versioned prompt configs. |

**Gate result**: ✅ All gates pass. Proceeding to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-docforge-publishing-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── http-api.md      # REST API contract
│   ├── ai-provider.md   # AI provider Python interface
│   ├── image-provider.md # Image provider Python interface
│   └── plugin-manifest.md # Plugin manifest schema
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
docforge/
├── __init__.py
├── ai/                  # AI provider abstraction + adapters
│   ├── base.py          # AIProvider interface
│   ├── openai_adapter.py
│   └── prompts/         # Versioned prompt YAML configs
├── cache/               # Cache backend abstraction
│   ├── base.py
│   └── filesystem.py
├── cli/                 # CLI commands (Typer)
│   ├── main.py          # Entry point
│   ├── render.py
│   ├── analyse.py
│   ├── init.py
│   ├── doctor.py
│   └── ...
├── config/              # Config loading, validation, profiles
│   ├── loader.py
│   ├── schema.py        # Pydantic config models
│   └── profiles/        # Built-in YAML profiles
├── core/                # Domain models (pure Python, no I/O)
│   ├── document.py      # SemanticModel, Chapter, Paragraph, etc.
│   ├── rendering.py     # RenderingDecision, RenderingJob, RenderEstimate
│   └── project.py       # Project, UserAccount
├── document/            # Document loader & analyser
│   ├── loader.py
│   └── analyser.py
├── exporters/           # Export format adapters
│   └── docx.py
├── images/              # Photo pipeline
│   ├── base.py          # ImageProvider interface
│   ├── wikimedia.py
│   ├── unsplash.py
│   ├── pexels.py
│   ├── downloader.py
│   ├── optimiser.py
│   └── licence.py
├── logging/             # Structured logging setup
│   └── setup.py
├── plugins/             # Plugin registry and lifecycle
│   ├── registry.py
│   └── manifest.py
├── rendering/           # Rendering engine
│   ├── engine.py
│   ├── theme_resolver.py
│   └── layout_validator.py
├── server/              # FastAPI HTTP layer
│   ├── app.py
│   ├── auth.py          # Login, session tokens, user account
│   ├── routers/
│   │   ├── documents.py
│   │   ├── jobs.py
│   │   ├── projects.py
│   │   └── system.py
│   └── store.py         # SQLite project store
├── templates/           # Template engine
│   └── engine.py
├── themes/              # Built-in theme YAML definitions
│   ├── minimal.yaml
│   ├── national_geographic.yaml
│   └── ...
└── validation/          # Validation framework
    └── pipeline.py

tests/
├── unit/                # Pure logic, no I/O
├── integration/         # Real DB, mocked external providers
├── rendering/           # Rendering pipeline tests
├── golden/              # Golden document reference tests
│   └── fixtures/
└── e2e/                 # Full pipeline end-to-end

prompts/                 # Versioned prompt YAML configs (outside package)
docs/
examples/
scripts/
```

**Structure Decision**: Single Python package (`docforge/`) with layered internal modules.
The `server/` module is a thin FastAPI adapter on top of `core/` + `rendering/`. The CLI
(`cli/`) is implemented entirely through the public Python API. No circular dependencies
are permitted; `core/` has zero infrastructure imports.

---

## Complexity Tracking

No constitution violations requiring justification.
