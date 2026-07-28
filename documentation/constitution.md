# Constitution

**Project:** DocForge

**Version:** 1.0

**Status:** Draft

---

# 1. Vision

DocForge exists to transform ordinary Microsoft Word documents into publication-quality documents through deterministic software engineering rather than manual editing.

The project is built on one simple idea:

> A professionally designed document should be reproducible.

Every design decision must be explainable, repeatable, configurable and testable.

The purpose of DocForge is **not** to replace graphic designers.

The purpose is to automate everything that can be automated while preserving professional quality.

The system should produce documents that are visually comparable with commercial publications while remaining completely reproducible.

No manual editing should be required after successful execution.

---

# 2. Mission

DocForge is an open platform for automated editorial publishing.

Its mission is to combine:

- structured document analysis
- deterministic document rendering
- configurable visual themes
- responsible use of AI
- legal image sourcing
- production-quality typography

into one coherent publishing pipeline.

The project shall remain independent from any specific AI vendor.

The project shall remain independent from any specific cloud provider.

The project shall remain independent from any specific document template.

---

# 3. Core Philosophy

## 3.1 Software First

Every feature should first be implemented through deterministic software.

Artificial Intelligence must never replace deterministic behaviour when deterministic behaviour is possible.

AI is responsible for judgement.

Software is responsible for execution.

Example:

AI decides:

- image placement
- page balance
- sidebar usage
- typography adjustments

Software performs:

- DOCX modification
- image insertion
- table formatting
- style application

The AI never edits the document directly.

---

## 3.2 Deterministic Rendering

Given:

- identical input
- identical configuration
- identical template
- identical assets

the system must produce identical output.

Rendering should be reproducible.

Randomness must never affect layout.

---

## 3.3 Explainable Decisions

Every AI decision should be explainable.

The system should be capable of producing structured reasoning such as:

- why this photograph was selected
- why this layout was chosen
- why this sidebar was inserted
- why this colour was applied

This information should be available through logs.

---

## 3.4 Human Ownership

The author's work belongs to the author.

DocForge never becomes an author.

DocForge never rewrites content.

DocForge never changes historical facts.

DocForge never changes recommendations.

DocForge never changes writing style.

DocForge only changes presentation.

---

# 4. Architectural Principles

The architecture shall be modular.

Every subsystem should have exactly one responsibility.

Subsystems communicate only through explicit interfaces.

Hidden coupling is forbidden.

Circular dependencies are forbidden.

Business logic shall never depend on infrastructure.

Infrastructure may depend on business logic.

---

# 5. Separation of Responsibilities

The system consists of independent domains.

## Document Engine

Responsible for:

- reading DOCX
- writing DOCX
- styles
- tables
- images
- headers
- footers
- sections
- page breaks

The Document Engine knows nothing about AI.

---

## AI Engine

Responsible only for decisions.

The AI Engine never edits documents.

It only produces structured instructions.

Example:

```json
{
  "insert_sidebar": true,
  "sidebar_style": "tip",
  "photo_layout": "two-column",
  "heading_color": "olive"
}
```

---

## Rendering Engine

Consumes:

- document
- template
- AI instructions

Produces:

finished publication.

---

## Photo Engine

Responsible for:

- searching
- downloading
- validating
- licensing
- caching
- resizing
- optimisation

The Photo Engine knows nothing about document rendering.

---

## Template Engine

Responsible only for visual identity.

Examples:

- National Geographic
- Lonely Planet
- Minimal
- Corporate
- Magazine

A template must never contain business logic.

---

# 6. Dependency Rule

Dependencies must point inward.

```
CLI
↓

Application

↓

Domain

↓

Infrastructure
```

Infrastructure never defines business rules.

Business rules never depend on infrastructure.

---

# 7. AI Independence

The project shall never depend on one LLM provider.

Supported providers should include:

- OpenAI
- Anthropic
- Google Gemini
- Ollama
- OpenRouter

Adding a new provider must require only a new adapter.

Business logic must remain unchanged.

---

# 8. Prompt Independence

Prompts are configuration.

Prompts are not code.

Changing prompts must never require changing business logic.

Prompts should be stored separately.

They should be versioned.

They should be testable.

---

# 9. Template Independence

Themes are configuration.

Themes are not code.

Every visual template should be replaceable without modifying rendering logic.

Templates define:

- colours
- typography
- spacing
- borders
- icons
- page decorations

Templates never define behaviour.

---

# 10. Image Provider Independence

The system shall support multiple providers.

Preferred providers:

- Wikimedia Commons
- Official tourism portals
- Unsplash
- Pexels

Providers are plugins.

Adding a provider must not require changing business logic.

---

# 11. Licensing Policy

Copyright compliance is mandatory.

The system must never knowingly embed copyrighted images without permission.

Preferred licences:

- Public Domain
- CC0
- CC BY
- CC BY-SA

When licence information is unavailable:

the image shall not be embedded automatically.

Instead, the placeholder should remain.

Every embedded image must have traceable provenance.

The final document should contain an appendix listing:

- image
- source
- author
- licence
- URL

---

# 12. Security Principles

The system must never execute downloaded code.

The system must never trust remote metadata.

Every downloaded asset must be validated.

Only supported image formats shall be accepted.

Downloaded content should be scanned for corruption before processing.

Temporary files must be isolated.

Secrets must never appear in logs.

API keys must only be loaded through secure configuration.

---

# 13. Configuration Philosophy

Everything configurable should be configuration.

Nothing configurable should require code changes.

Configuration should support:

- YAML
- TOML

Environment variables should override configuration files.

Command-line arguments should override both.

Configuration must be validated before execution.

Invalid configuration must stop execution.

# 14. Quality Gates

Every release must satisfy mandatory quality gates before publication.

Quality gates are considered part of the architecture rather than the development process.

A release that fails a quality gate shall not be published.

---

## 14.1 Functional Quality

Every public feature shall have:

- automated tests
- documented behaviour
- deterministic output
- configuration examples

---

## 14.2 Visual Quality

Every generated document shall be reviewed through automated visual validation.

Validation should verify:

- page balance
- spacing consistency
- heading hierarchy
- table formatting
- image placement
- page breaks
- typography

Visual regressions are considered software defects.

---

## 14.3 Licensing Quality

Every embedded image must have traceable provenance.

Images without verified licensing information shall never be embedded automatically.

The generated Image Sources appendix is mandatory.

---

## 14.4 Documentation Quality

Public APIs, CLI commands and configuration options shall be documented before release.

Documentation is part of the product.

---

# 15. Testing Philosophy

Testing is a first-class feature.

Every bug fixed shall produce at least one new automated test.

The preferred testing pyramid is:

- unit tests
- integration tests
- rendering tests
- end-to-end tests

Manual testing should be the exception.

---

## 15.1 Golden Document Testing

Golden documents are canonical reference documents.

Given identical:

- input document
- configuration
- template
- image cache

the renderer shall produce byte-equivalent or semantically equivalent output.

Unexpected rendering changes must be reviewed.

---

## 15.2 Snapshot Testing

The project shall maintain visual snapshots.

Each release should compare rendered pages against reference pages.

Large visual differences should fail CI.

---

# 16. Error Handling

The system must fail gracefully.

A single missing image must never terminate the entire rendering pipeline.

Recoverable errors should produce warnings.

Irrecoverable errors should stop execution with clear diagnostics.

Users should always know:

- what failed
- why it failed
- how to fix it

---

# 17. Logging and Observability

Logging is a product feature.

The system shall support multiple verbosity levels.

Every execution should produce a structured log describing:

- document loading
- template selection
- AI provider
- prompt version
- rendering decisions
- image downloads
- licence verification
- caching
- warnings
- failures

Logs should be machine-readable.

JSON logging should be supported.

---

# 18. Performance Principles

Performance must scale with document size.

The renderer should avoid repeated work.

Caching is mandatory wherever practical.

The system should:

- reuse downloaded images
- reuse AI responses when possible
- avoid duplicate parsing
- avoid unnecessary document rewrites

Performance optimizations must never reduce correctness.

---

# 19. Plugin Architecture

Everything that may evolve independently should be implemented as a plugin.

Examples include:

- AI providers
- image providers
- templates
- export formats
- document analysers

Plugins shall expose stable interfaces.

Plugins shall never bypass the public API.

---

# 20. Public API Principles

The Python API is a supported product.

Public interfaces must remain stable.

Breaking API changes require a major version.

Internal implementation details must remain private.

Public APIs should prioritize clarity over cleverness.

---

# 21. Command Line Interface

The CLI is a first-class interface.

It should be suitable for:

- local usage
- automation
- CI/CD
- GitHub Actions
- scripting

CLI commands should be predictable and composable.

Machine-readable output should be available where appropriate.

---

# 22. Configuration Compatibility

Configuration files represent user intent.

Backward compatibility should be preserved whenever possible.

When configuration changes are required:

- provide migration guidance
- issue deprecation warnings
- support transition periods

Silent configuration changes are prohibited.

---

# 23. Versioning

The project shall follow Semantic Versioning.

Major versions indicate breaking changes.

Minor versions introduce backwards-compatible functionality.

Patch versions contain bug fixes only.

Templates and prompts should also be versioned independently.

---

# 24. Dependency Management

Dependencies are liabilities.

Every dependency must have a clear justification.

Prefer mature, actively maintained libraries.

Avoid unnecessary transitive dependencies.

Vendor code only when absolutely necessary.

---

# 25. Coding Standards

Code shall prioritize readability over brevity.

Preferred characteristics:

- explicit
- deterministic
- testable
- documented
- maintainable

Avoid hidden side effects.

Avoid global mutable state.

Type annotations are mandatory for public APIs.

Static analysis should pass without warnings.

---

# 26. Documentation Standards

Every public module shall include documentation.

Examples should accompany complex features.

Configuration examples should be complete and executable.

Documentation must evolve together with the codebase.

Outdated documentation is considered a defect.

---

# 27. Accessibility

Generated documents should be readable both digitally and when printed.

Design choices should consider:

- contrast
- font size
- whitespace
- readability
- colour accessibility

Decorative elements must never reduce readability.

---

# 28. Internationalization

The system must support multiple document languages.

Language-specific conventions should be configurable.

Typography, quotation marks, dates, captions and automatically generated text must follow the conventions of the selected language.

The rendering engine shall never assume English as the default content language.

---

# 29. Future Evolution

Future development shall extend the system through composition rather than modification.

Whenever possible:

- add plugins
- add providers
- add templates

Avoid changing existing stable behaviour.

Backward compatibility is preferred over architectural purity.

---

# 30. Definition of Done

A feature is considered complete only when all of the following are true:

✓ implementation completed

✓ automated tests added

✓ documentation updated

✓ configuration documented

✓ examples provided

✓ visual rendering verified

✓ licensing verified

✓ code review completed

✓ static analysis passed

✓ CI passed

✓ no critical warnings remain

Features that fail any criterion are incomplete.

---

# 31. Long-Term Vision

DocForge is intended to become a general-purpose document publishing platform rather than a travel-guide-specific application.

The architecture should support future domains including, but not limited to:

- books
- reports
- technical documentation
- magazines
- educational materials
- research papers
- annual reports
- marketing collateral

No architectural decision should unnecessarily constrain future expansion.

---

# 32. Constitutional Amendment Process

This Constitution is a living document.

Amendments shall be conservative.

Every amendment must satisfy the following principles:

1. Preserve backward compatibility whenever feasible.
2. Improve long-term maintainability.
3. Avoid increasing architectural complexity without clear justification.
4. Maintain the separation between business logic and infrastructure.
5. Keep AI advisory and deterministic software authoritative for execution.

Major amendments should be reviewed alongside their architectural rationale and expected long-term impact.

---

# Closing Statement

DocForge exists to demonstrate that document publishing can be engineered with the same discipline applied to modern software systems.

Automation should increase quality rather than reduce it.

Artificial Intelligence should amplify professional judgement rather than replace craftsmanship.

Every generated document should reflect the principles of reproducibility, legality, maintainability, and editorial excellence.

The Constitution defines enduring principles.

Implementation details may evolve.

These principles shall remain.
