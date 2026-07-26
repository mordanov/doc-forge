# DocForge

An AI-assisted editorial publishing platform that transforms Microsoft Word documents into publication-quality outputs using deterministic rendering and AI-driven editorial decisions.

---

## Overview

DocForge automates professional document layout while preserving author content. It accepts a `.docx` file and produces a polished publication with styled typography, automatically sourced and licensed photographs, generated covers, tables of contents, headers, footers, and image attribution appendices.

DocForge is a publishing pipeline — not a text editor, not a document author, not a desktop publishing application.

---

## Features

- DOCX input and output
- AI-assisted editorial decisions (layout, typography, image placement)
- Automatic image search, licence validation, download, and optimisation
- Configurable themes (Minimal, National Geographic, Lonely Planet, DK Eyewitness, Corporate, and more)
- Cover page generation
- Table of contents generation
- Headers, footers, and page numbering
- Image attribution appendix
- Multi-language support (Russian, English, Spanish, German, French)
- Deterministic, reproducible rendering
- Offline mode with cached assets
- Plugin architecture for providers, themes, and exporters
- CLI and Python API

---

## Tech Stack

### Frontend

| Layer | Technology |
|---|---|
| Framework | React 19 |
| Language | TypeScript |
| Build | Vite |
| Styling | TailwindCSS |
| Components | shadcn/ui |
| Forms | React Hook Form + Zod |
| Data fetching | TanStack Query |
| Routing | React Router |
| Icons | Lucide Icons |
| Animations | Framer Motion |
| State | Zustand |
| Charts | Recharts |

### Backend

| Layer | Technology |
|---|---|
| Language | Python |
| AI Providers | OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama |
| Image Providers | Wikimedia Commons, Official Sources, Unsplash, Pexels |
| Document engine | python-docx |
| Cache backends | Filesystem (v1), Redis / S3 / Azure Blob / GCS (future) |

---

## Project Structure

```
doc-forge/
├── frontend/                  # React application
│   ├── src/
│   │   ├── app/               # App entry, router, providers
│   │   ├── features/          # Feature modules
│   │   │   ├── home/
│   │   │   ├── projects/
│   │   │   ├── wizard/        # New project wizard (5 steps)
│   │   │   ├── settings/
│   │   │   └── about/
│   │   ├── components/        # Shared UI components
│   │   ├── hooks/             # Shared hooks
│   │   ├── lib/               # Utilities, API client, validators
│   │   ├── store/             # Zustand stores
│   │   └── types/             # Shared TypeScript types
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── docforge/                  # Python backend package
│   ├── ai/                    # AI provider abstraction
│   ├── cache/                 # Cache backends
│   ├── cli/                   # CLI commands
│   ├── config/                # Configuration system
│   ├── core/                  # Application and domain layer
│   ├── document/              # Loader, analyser, internal model
│   ├── exporters/             # DOCX, PDF, HTML, EPUB, Markdown
│   ├── images/                # Photo subsystem
│   ├── logging/               # Structured logging
│   ├── plugins/               # Plugin registry and lifecycle
│   ├── rendering/             # Rendering engine
│   ├── templates/             # Theme manifests and assets
│   ├── themes/                # Theme engine
│   └── validation/            # Validation framework
│
├── tests/                     # All test suites
│   ├── unit/
│   ├── integration/
│   ├── rendering/
│   ├── golden/
│   └── e2e/
│
├── docs/                      # Documentation
├── examples/                  # Example documents and configurations
├── scripts/                   # Developer scripts
└── documentation/             # Architecture specifications
    ├── constitution.md
    ├── initial-specification.md
    └── frontend-specification.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- `uv` or `pip`

### Backend

```bash
# Install dependencies
uv sync

# Run CLI
docforge --help

# Render a document
docforge render input.docx output.docx

# Check runtime readiness
docforge doctor
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Configuration

Create a `docforge.yaml` in your project directory:

```yaml
project:
  language: en
  template: national_geographic

rendering:
  generate_cover: true
  generate_toc: true
  update_page_numbers: true

images:
  enabled: true
  provider_priority:
    - wikimedia
    - official
    - unsplash

ai:
  provider: openai
  prompt_set: editorial_v1

logging:
  level: INFO
```

Set API credentials via environment variables:

```bash
export OPENAI_API_KEY=sk-...
export UNSPLASH_ACCESS_KEY=...
export PEXELS_API_KEY=...
```

---

## CLI Reference

| Command | Description |
|---|---|
| `docforge render` | Render a document |
| `docforge analyse` | Analyse document structure |
| `docforge validate` | Validate configuration and document |
| `docforge themes` | List available themes |
| `docforge cache` | Manage cache |
| `docforge prompts` | List prompt versions |
| `docforge providers` | List configured providers |
| `docforge doctor` | Check runtime readiness |
| `docforge version` | Show version |
| `docforge config` | Show resolved configuration |
| `docforge export` | Export to additional formats |
| `docforge images` | Manage image assets |
| `docforge clean` | Clean cache and temporary files |

---

## Python API

```python
from docforge import Renderer

# Simple usage
renderer = Renderer()
renderer.render(
    input_path="guide.docx",
    output_path="guide_final.docx"
)

# Fluent API
(
    Renderer()
        .template("national_geographic")
        .language("ru")
        .provider("openai")
        .render(
            input_path="guide.docx",
            output_path="guide_final.docx"
        )
)
```

---

## Frontend Pages

| Page | Description |
|---|---|
| Home | Landing page with recent projects and drag-and-drop upload |
| New Project | 5-step wizard: Upload → AI Config → Publication Config → Preview → Render |
| Projects | List of all publications with status and actions |
| Settings | Global application settings |
| About | Version, documentation, licences, contributors |

---

## Themes

| Theme | Description |
|---|---|
| Minimal | Clean, distraction-free layout |
| Modern | Contemporary editorial style |
| Classic | Traditional book layout |
| National Geographic | Rich photography-forward design |
| Lonely Planet | Travel guide with colourful accents |
| DK Eyewitness | Structured editorial with sidebars |
| Magazine | Editorial magazine layout |
| Corporate | Professional business document |
| Luxury | Premium typographic treatment |
| Academic | Scholarly paper formatting |
| Pop Art | Bold, expressive design |
| Scandinavian | Minimal, high-contrast Nordic style |
| Vintage | Heritage editorial aesthetic |
| Newspaper | Classic broadsheet layout |
| Children | Friendly, playful design |
| Travel Blog | Relaxed, image-rich layout |

---

## AI Providers

DocForge uses AI exclusively for editorial decisions. The AI never modifies document content.

| Provider | Status |
|---|---|
| OpenAI | Supported (v1) |

---

## Image Licences

Only legally reusable images are embedded. Supported licences:

- Public Domain
- CC0
- CC BY
- CC BY-SA

Every generated publication includes an **Image Sources** appendix with full attribution.

---

## Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# Golden document tests
pytest tests/golden
```

Coverage target: 95%+ overall, 100% for business logic.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Ensure all CI checks pass before opening a pull request
4. No pull request may be merged while mandatory checks fail

Static analysis tools in use: Ruff, MyPy, Bandit, Pre-commit.

---

## Architecture

DocForge follows a strict layered architecture:

```
CLI / Python API
       ↓
Application Layer
       ↓
Domain Layer
       ↓
Rendering Layer
       ↓
Infrastructure Layer
```

Each layer communicates only with adjacent layers. The AI subsystem acts as an advisory service and never directly manipulates documents. All document modifications are performed by the deterministic rendering engine.

Full architectural principles are defined in `documentation/constitution.md`.
Full implementation requirements are defined in `documentation/initial-specification.md`.

---

## Licence

To be defined.
