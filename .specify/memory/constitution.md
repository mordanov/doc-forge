<!--
SYNC IMPACT REPORT
==================
Version change: [placeholder/0.0.0] → 1.0.0
Bump rationale: MAJOR — first substantive population of all placeholder tokens from
                source constitution at documentation/constitution.md.

Modified principles:
  All placeholder sections replaced with concrete DocForge principles.

Added sections:
  - I. Software First
  - II. Deterministic Rendering
  - III. Human Ownership
  - IV. Modular Independence
  - V. Legal Compliance
  - VI. Quality Gates & Definition of Done
  - VII. Security
  - VIII. Configuration Over Code
  - Architecture & Technology Standards
  - Development Quality & Process

Removed sections: N/A (template placeholders replaced)

Templates reviewed:
  ✅ .specify/templates/plan-template.md  — Constitution Check section already generic; no change required
  ✅ .specify/templates/spec-template.md  — template is generic; aligns with principles
  ✅ .specify/templates/tasks-template.md — task categories align with new principles
  ⚠  .specify/templates/commands/         — directory not found; no command templates to update

Deferred TODOs:
  - RATIFICATION_DATE set to first-population date 2026-07-26 (original authorship date unknown)
-->

# DocForge Constitution

## Core Principles

### I. Software First

Deterministic software is authoritative for execution; AI is strictly advisory.

- Every feature MUST first be implemented through deterministic software.
- AI MUST NOT replace deterministic behaviour when deterministic behaviour is possible.
- AI produces structured instructions (JSON decisions); software executes them.
- The AI Engine MUST NEVER edit documents directly.
- AI decisions MUST be explainable and logged with structured reasoning.

**Rationale**: Reproducibility and correctness require execution to be deterministic.
Non-deterministic AI in the execution path would make output unpredictable and untestable.

---

### II. Deterministic Rendering

Given identical input, configuration, template, and assets — the system MUST produce identical output.

- Randomness MUST NEVER affect layout or rendering.
- Rendering MUST be reproducible across runs, environments, and versions.
- Visual regressions are considered software defects and MUST fail CI.
- Golden document tests MUST pass for every release.

**Rationale**: Publication quality requires reproducibility. Any non-determinism makes
automated visual validation impossible and erodes user trust.

---

### III. Human Ownership

The author's work belongs to the author. DocForge changes presentation only — never content.

- DocForge MUST NEVER rewrite content, change historical facts, change recommendations,
  or alter writing style.
- DocForge MUST NEVER become an author or co-author.
- All changes are scoped to visual presentation: layout, typography, images, styling.

**Rationale**: Preserving author intent is a non-negotiable ethical and legal requirement.
Any content mutation would undermine trust and potentially introduce liability.

---

### IV. Modular Independence

Every subsystem has exactly one responsibility and communicates only through explicit interfaces.

- Hidden coupling is forbidden. Circular dependencies are forbidden.
- Business logic MUST NEVER depend on infrastructure. Infrastructure MAY depend on business logic.
- Dependencies MUST point inward: CLI → Application → Domain → Infrastructure.
- Each engine (Document, AI, Rendering, Photo, Template) MUST be replaceable independently.
- The system MUST support multiple AI providers, image providers, and templates as plugins.
  Adding any new provider or template MUST require only a new adapter — no business logic changes.

**Rationale**: Modularity enables independent testing, replacement, and future evolution
without cascading changes across the codebase.

---

### V. Legal Compliance

Copyright compliance is mandatory. The system MUST NEVER knowingly embed copyrighted images
without permission.

- Preferred licences: Public Domain, CC0, CC BY, CC BY-SA.
- Images without verified licensing information MUST NOT be embedded automatically;
  a placeholder MUST remain instead.
- Every embedded image MUST have traceable provenance.
- The final document MUST contain an Image Sources appendix listing image, source, author,
  licence, and URL.
- The Image Sources appendix is a mandatory quality gate — a release without it MUST NOT ship.

**Rationale**: Legal exposure from unlicensed images would be a critical business and
reputational risk. Provenance tracking is both an ethical obligation and a legal safeguard.

---

### VI. Quality Gates & Definition of Done

A feature is complete only when all gates pass. A release that fails any gate MUST NOT be published.

Mandatory gates per feature:
- Automated tests covering the public behaviour
- Documented behaviour and configuration examples
- Visual rendering verified (page balance, spacing, typography, image placement)
- Licensing verified for all embedded assets
- Code review completed; static analysis passed without warnings
- CI passed; no critical warnings remain

Mandatory testing pyramid:
- Unit tests → Integration tests → Rendering/golden-document tests → End-to-end tests
- Every bug fixed MUST produce at least one new automated test.
- Manual testing MUST be the exception, not the norm.

**Rationale**: Automating quality enforcement prevents regressions and ensures that
"done" means the same thing for every feature and every release.

---

### VII. Security

The system MUST handle external content safely at all boundaries.

- The system MUST NEVER execute downloaded code.
- The system MUST NEVER trust remote metadata without validation.
- Every downloaded asset MUST be validated; only supported image formats shall be accepted.
- Temporary files MUST be isolated.
- Secrets MUST NEVER appear in logs.
- API keys MUST only be loaded through secure configuration (environment variables or
  secrets management); never hardcoded.

**Rationale**: DocForge processes external assets and calls third-party APIs. A single
boundary violation could expose user systems or credentials.

---

### VIII. Configuration Over Code

Everything configurable MUST be configuration — no configurable behaviour requires code changes.

- Prompts are configuration, not code. Changing prompts MUST NOT require changing business logic.
- Templates are configuration, not code. Every visual template MUST be replaceable without
  modifying rendering logic.
- Configuration MUST support YAML and TOML formats.
- Precedence: command-line arguments > environment variables > configuration files.
- Configuration MUST be validated before execution. Invalid configuration MUST stop execution
  with clear diagnostics.
- Backward compatibility of configuration files MUST be preserved whenever possible;
  breaking changes require migration guidance, deprecation warnings, and transition periods.

**Rationale**: Separating configuration from code enables non-developer customisation,
A/B testing of prompts and templates, and independent versioning of each layer.

---

## Architecture & Technology Standards

**Project type**: CLI tool + Python library + optional web frontend (React/TypeScript)

**Language/Runtime**: Python (backend/core); React 19 + TypeScript (frontend)

**AI Providers**: OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama — all via adapters.
The project MUST remain independent from any single AI vendor.

**Image Providers**: Wikimedia Commons, Official tourism portals, Unsplash, Pexels — all as plugins.

**Document Engine**: python-docx for DOCX read/write; no other document engine shall be assumed.

**Dependency policy**: Every dependency MUST have a clear justification. Prefer mature,
actively maintained libraries. Avoid unnecessary transitive dependencies.

**Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH). Templates and prompts MUST also be
versioned independently. Breaking API changes require a MAJOR version bump.

**Internationalization**: The rendering engine MUST NEVER assume English as the default
content language. Typography, quotation marks, dates, captions, and auto-generated text
MUST follow the conventions of the selected language.

---

## Development Quality & Process

**Logging**: Every execution MUST produce a structured log. JSON logging MUST be supported.
Verbosity levels MUST be configurable. Logs MUST capture: document loading, template selection,
AI provider, prompt version, rendering decisions, image downloads, licence verification,
caching, warnings, and failures.

**Error handling**: The system MUST fail gracefully. A single missing image MUST NEVER
terminate the entire pipeline. Recoverable errors produce warnings; irrecoverable errors
stop execution with clear user-facing diagnostics (what failed, why, how to fix).

**Performance**: Caching is mandatory wherever practical. Downloaded images, AI responses
(where appropriate), and parsed documents MUST be reused across invocations.
Performance optimisations MUST NEVER reduce correctness.

**Accessibility**: Generated documents MUST be readable both digitally and when printed.
Design choices MUST consider contrast, font size, whitespace, readability, and colour
accessibility. Decorative elements MUST NEVER reduce readability.

**Public API**: The Python API is a supported product. Public interfaces MUST remain stable;
internal implementation details MUST remain private. Type annotations are mandatory for
public APIs. Static analysis MUST pass without warnings.

**CLI**: The CLI is a first-class interface suitable for local use, automation, CI/CD,
GitHub Actions, and scripting. Commands MUST be predictable, composable, and offer
machine-readable output where appropriate.

**Future evolution**: New functionality MUST be added through composition (plugins, providers,
templates), not modification of stable behaviour. Backward compatibility is preferred over
architectural purity.

---

## Governance

This Constitution supersedes all other practices and guidelines within the DocForge project.

**Amendment procedure**:
1. Every amendment MUST preserve backward compatibility whenever feasible.
2. Every amendment MUST improve long-term maintainability.
3. No amendment may increase architectural complexity without clear justification.
4. The separation between business logic and infrastructure MUST be maintained.
5. AI MUST remain advisory; deterministic software MUST remain authoritative for execution.
6. Major amendments MUST be reviewed alongside their architectural rationale and expected
   long-term impact.

**Versioning policy**: Constitution version follows Semantic Versioning.
- MAJOR: backward-incompatible governance or principle removals / redefinitions.
- MINOR: new principle or section added, or material expansion of guidance.
- PATCH: clarifications, wording, or non-semantic refinements.

**Compliance**: All implementation plans, specifications, and code reviews MUST verify
compliance with this Constitution before proceeding. The Constitution Check section of
every plan.md is mandatory.

**Runtime guidance**: For project-specific runtime guidance, refer to `CLAUDE.md`
and `.specify/` documentation.

---

**Version**: 1.0.0 | **Ratified**: 2026-07-26 | **Last Amended**: 2026-07-26
