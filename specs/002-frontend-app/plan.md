# Implementation Plan: DocForge Frontend Application

**Branch**: `002-frontend-app` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-frontend-app/spec.md`

## Summary

Build a production-quality React 19 + TypeScript SPA that provides the full user interface for DocForge. The frontend delegates all document rendering to the existing FastAPI backend. The primary feature is a 5-step wizard (Upload → AI Config → Publication Config → Preview → Render) that guides users from document upload to downloadable publication. Secondary features are a Projects list with CRUD actions, Settings persistence, and an About page.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 20 LTS
**Framework**: React 19 + Vite 6
**UI Library**: TailwindCSS 3 + shadcn/ui (Radix primitives)
**State**: Zustand (auth + theme + wizard draft), TanStack Query v5 (server state)
**Routing**: React Router v6.4+ (`createBrowserRouter`)
**Forms**: React Hook Form + Zod
**Animation**: Framer Motion
**Icons**: Lucide React
**HTTP**: Axios + TanStack Query
**Testing**: Vitest + React Testing Library + Playwright + MSW
**Storage**: `localStorage` for auth token and settings; `sessionStorage` for wizard draft
**Target Platform**: Desktop/laptop browsers (Chrome, Firefox, Safari, Edge); 13"+ screen
**Performance Goals**: All pages interactive in < 2 seconds on standard broadband; form validation feedback within 1 second
**Constraints**: WCAG AA accessibility; dark/light mode with zero flash-of-wrong-theme; no server-side rendering
**Scale/Scope**: Single-user (admin); 5 pages; 5-step wizard; ~40 React components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Software First | ✅ Pass | Frontend delegates all rendering to backend; no AI logic in the UI |
| II. Deterministic Rendering | ✅ Pass | Frontend is read-only display; rendering determinism is a backend concern |
| III. Human Ownership | ✅ Pass | Frontend never modifies document content; upload-and-display only |
| IV. Modular Independence | ✅ Pass | Feature-based folder structure; API layer is independent of UI; stores independent of components |
| V. Legal Compliance | ✅ Pass | Frontend displays licence summaries; does not embed images itself |
| VI. Quality Gates | ✅ Pass | Vitest + RTL for unit/component; Playwright for E2E; MSW for API mocking |
| VII. Security | ✅ Pass | JWT stored in localStorage (acceptable for single-user desktop app); API key stored obfuscated; never logged |
| VIII. Configuration Over Code | ✅ Pass | `VITE_API_URL` env var; preset configs as data constants, not hardcoded logic |

No violations. No complexity tracking required.

## Project Structure

### Documentation (this feature)

```
specs/002-frontend-app/
├── plan.md              # This file
├── research.md          # Tech decisions and API audit
├── data-model.md        # TypeScript interfaces for all API types + frontend state
├── quickstart.md        # Integration scenarios and dev onboarding
├── contracts/
│   └── ui-contracts.md  # Component and API hook contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```
frontend/
├── index.html                 # Includes inline dark-mode script (no FOCT)
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── .env.example
├── package.json               # pnpm workspace
│
├── src/
│   ├── main.tsx               # App entry, MSW setup in dev
│   ├── App.tsx                # Router + QueryClientProvider + ThemeProvider
│   │
│   ├── app/
│   │   ├── router.tsx         # createBrowserRouter, lazy routes, AuthGuard
│   │   ├── AppLayout.tsx      # Persistent chrome: sidebar/nav, footer
│   │   └── AuthGuard.tsx      # Redirects unauthenticated users to /login
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── services/authService.ts
│   │   │   └── hooks/useLogin.ts
│   │   │
│   │   ├── home/
│   │   │   └── HomePage.tsx
│   │   │
│   │   ├── wizard/
│   │   │   ├── NewProjectWizard.tsx   # Root component, step router
│   │   │   ├── wizardStore.ts         # Zustand slice, sessionStorage persist
│   │   │   ├── steps/
│   │   │   │   ├── Step1Upload.tsx
│   │   │   │   ├── Step2AiConfig.tsx
│   │   │   │   ├── Step3PublicationConfig.tsx
│   │   │   │   ├── Step4Preview.tsx
│   │   │   │   └── Step5Rendering.tsx
│   │   │   ├── presets.ts            # Built-in preset data constants
│   │   │   └── services/
│   │   │       ├── documentsService.ts
│   │   │       ├── jobsService.ts
│   │   │       └── hooks/
│   │   │           ├── useUploadDocument.ts
│   │   │           ├── useAnalyseDocument.ts
│   │   │           ├── useSubmitJob.ts
│   │   │           ├── useEstimate.ts
│   │   │           └── useJob.ts        # includes polling logic
│   │   │
│   │   ├── projects/
│   │   │   ├── ProjectsPage.tsx
│   │   │   ├── ProjectCard.tsx
│   │   │   └── services/
│   │   │       ├── projectsService.ts
│   │   │       └── hooks/
│   │   │           ├── useProjects.ts
│   │   │           ├── useProject.ts
│   │   │           ├── useDuplicateProject.ts
│   │   │           └── useDeleteProject.ts
│   │   │
│   │   ├── settings/
│   │   │   ├── SettingsPage.tsx
│   │   │   └── settingsStore.ts     # localStorage persist
│   │   │
│   │   └── about/
│   │       └── AboutPage.tsx
│   │
│   ├── components/
│   │   ├── ui/                      # shadcn generated — treat as read-only
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── select.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── switch.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   └── tooltip.tsx
│   │   │
│   │   ├── UploadArea.tsx           # Drag-and-drop, validates type and size
│   │   ├── ProgressTimeline.tsx     # Render stages with icon/progress/elapsed
│   │   ├── ThemeGallery.tsx         # Theme cards with preview + description
│   │   ├── PresetSelector.tsx       # Preset cards
│   │   ├── CostCard.tsx             # Estimate summary panel
│   │   ├── StatisticsCard.tsx       # Single-metric display
│   │   ├── ProjectCard.tsx          # Project list item (shared with feature)
│   │   ├── WizardNav.tsx            # Step indicator + back/next buttons
│   │   ├── ColourPicker.tsx         # Shown when palette = Custom
│   │   └── ErrorBoundary.tsx
│   │
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   ├── useMediaQuery.ts
│   │   └── useTheme.ts             # Read/write theme preference
│   │
│   ├── lib/
│   │   ├── api.ts                  # Axios instance + auth interceptor + 401 handler
│   │   ├── queryClient.ts          # TanStack QueryClient config
│   │   └── utils.ts                # cn(), formatters, parse helpers
│   │
│   ├── stores/
│   │   ├── authStore.ts            # JWT token, user info, logout
│   │   └── themeStore.ts           # 'light' | 'dark', persisted
│   │
│   └── types/
│       ├── api.ts                  # All backend response/request types (from data-model.md)
│       └── ui.ts                   # Frontend-only types (WizardDraft, Preset, AppSettings)
│
├── tests/
│   ├── unit/                       # Vitest: hooks, utils, stores
│   ├── component/                  # Vitest + RTL: component rendering and interactions
│   └── e2e/                        # Playwright: full browser tests against running backend
│
├── public/
│   └── theme-previews/             # Static preview images keyed by theme ID
│
└── src/mocks/
    ├── browser.ts                  # MSW browser worker
    ├── server.ts                   # MSW Node server (for Vitest)
    └── handlers.ts                 # All endpoint mocks
```

**Structure Decision**: Feature-based hybrid. Feature folders own their domain code; shared primitives live at `src/components/` and `src/lib/`. This layout scales cleanly to the 5-page scope without premature abstraction.

## Architecture Decisions

### Dark Mode — No Flash of Wrong Theme

Add this inline script to `index.html` before the React bundle loads:

```html
<script>
  (function() {
    var theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') document.documentElement.classList.add('dark');
  })();
</script>
```

### Job Polling

`useJob` uses TanStack Query's `refetchInterval`:

```typescript
useQuery({
  queryKey: ['job', jobId],
  queryFn: () => jobsService.getJob(jobId),
  refetchInterval: (data) =>
    data && ['COMPLETED', 'FAILED', 'CANCELLED'].includes(data.status)
      ? false   // stop polling
      : 3000,   // poll every 3 seconds
})
```

### Theme Display Names

The backend returns theme `id` only (no `name` or `description`). Maintain a frontend constant map:

```typescript
export const THEME_METADATA: Record<string, { name: string; description: string }> = {
  minimal:            { name: 'Minimal',         description: 'Clean, typography-focused layout' },
  dk_eyewitness:      { name: 'DK Eyewitness',   description: 'Rich imagery, structured sidebars' },
  lonely_planet:      { name: 'Lonely Planet',   description: 'Warm editorial travel style' },
  national_geographic:{ name: 'National Geographic', description: 'Dramatic full-bleed photography' },
  corporate:          { name: 'Corporate',        description: 'Professional business presentation' },
}
```

### API Response Normalisation

`output_paths` and `warnings` fields from `/jobs/{id}` are JSON-encoded strings. The API client normalises them before returning:

```typescript
function parseJob(raw: Job): ParsedJob {
  return {
    ...raw,
    output_paths: JSON.parse(raw.output_paths || '[]'),
    warnings: JSON.parse(raw.warnings || '[]'),
  }
}
```

## Complexity Tracking

No constitution violations. No exceptional complexity introduced.
