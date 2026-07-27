# Tasks: DocForge Frontend Application

**Input**: Design documents from `specs/002-frontend-app/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ui-contracts.md ✓, quickstart.md ✓

**Tests**: Test tasks are included in the Polish phase (Vitest + RTL + Playwright). They reflect the testing stack defined in plan.md and are scoped to cover the 8 quickstart integration scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths are included in every description

---

## Phase 1: Setup

**Purpose**: Project initialization and toolchain configuration. No user story work can begin until this phase is complete.

- [ ] T001 Scaffold Vite 6 + React 19 + TypeScript project in `frontend/` with pnpm (`pnpm create vite frontend --template react-ts`); verify `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json` are generated
- [ ] T002 [P] Install all runtime dependencies in `frontend/package.json`: `react-router-dom@6`, `@tanstack/react-query@5`, `zustand`, `axios`, `framer-motion`, `lucide-react`, `react-hook-form`, `zod`, `@hookform/resolvers`
- [ ] T003 [P] Install and configure TailwindCSS 3 with `darkMode: 'class'` strategy in `frontend/tailwind.config.ts`; add `@tailwind` directives to `frontend/src/index.css`
- [ ] T004 [P] Initialize shadcn/ui in `frontend/` (`pnpm dlx shadcn-ui@latest init`); add components: `button`, `card`, `dialog`, `dropdown-menu`, `input`, `label`, `select`, `slider`, `switch`, `tabs`, `toast`, `tooltip`
- [ ] T005 [P] Install dev dependencies in `frontend/package.json`: `vitest`, `@testing-library/react`, `@testing-library/user-event`, `msw@2`, `@playwright/test`; add `test` and `test:e2e` scripts
- [ ] T006 [P] Configure Vitest with jsdom environment and MSW setup in `frontend/vite.config.ts`; add `frontend/src/test-setup.ts`
- [ ] T007 [P] Configure Playwright in `frontend/playwright.config.ts` targeting `http://localhost:5173`; add `frontend/tests/e2e/` directory
- [ ] T008 [P] Create `frontend/.env.example` with `VITE_API_URL=http://localhost:8000`; create `frontend/.gitignore` covering `node_modules/`, `dist/`, `.env`, `playwright-report/`

**Checkpoint**: `pnpm dev` starts without errors, `pnpm test` runs (no test files yet, exits 0), `pnpm test:e2e` runs with no failures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that every user story depends on. No user story work can begin until this phase is complete.

**⚠️ CRITICAL**: All four user stories share the API client, type system, auth, theme, and app shell defined here.

- [ ] T009 Create all backend API type definitions in `frontend/src/types/api.ts`: `AuthToken`, `UploadedDocument`, `DocumentAnalysis`, `ValidationIssue`, `Job`, `ParsedJob`, `JobStatus`, `RenderStage`, `JobSubmitRequest`, `JobSubmitResponse`, `JobEstimate`, `Project`, `ParsedProject`, `Theme`, `ProvidersStatus`, `AIProviderStatus`, `ImageProviderStatus`, `HealthCheck`, `ApiError` — exact shapes from `data-model.md`
- [ ] T010 [P] Create frontend-only type definitions in `frontend/src/types/ui.ts`: `WizardDraft`, `WizardStep`, `OutputFormat`, `ImagePolicy`, `Preset`, `AppSettings` — exact shapes from `data-model.md`
- [ ] T011 Create Axios instance with `Authorization: Bearer` request interceptor and 401 → logout response interceptor in `frontend/src/lib/api.ts`; read `VITE_API_URL` from `import.meta.env`
- [ ] T012 [P] Create TanStack `QueryClient` with default `staleTime: 30_000` and `retry: 1` in `frontend/src/lib/queryClient.ts`
- [ ] T013 [P] Create utility functions in `frontend/src/lib/utils.ts`: `cn()` (clsx + tailwind-merge), `parseJob(raw: Job): ParsedJob` (parses `output_paths` and `warnings` JSON strings), `parseProject(raw: Project): ParsedProject`, `formatBytes()`, `formatDuration()`
- [ ] T014 Create auth Zustand store in `frontend/src/stores/authStore.ts`: state `{ token, isAuthenticated }`, actions `{ setToken, logout }`; persist `token` to `localStorage` key `"auth"`
- [ ] T015 [P] Create theme Zustand store in `frontend/src/stores/themeStore.ts`: state `{ theme: 'light' | 'dark' }`, action `{ setTheme }`; persist to `localStorage` key `"theme"`; on `setTheme`, toggle `document.documentElement.classList`
- [ ] T016 Create MSW request handlers for all endpoints in `frontend/src/mocks/handlers.ts`: `POST /auth/login`, `GET /system/health`, `GET /system/themes`, `GET /system/providers`, `POST /documents/upload`, `POST /documents/{id}/analyse`, `POST /jobs`, `GET /jobs/{id}`, `POST /jobs/estimate`, `GET /projects`, `GET /projects/{id}`, `POST /projects/{id}/duplicate`, `DELETE /projects/{id}`, `GET /jobs/{id}/download`
- [ ] T017 [P] Create MSW browser worker in `frontend/src/mocks/browser.ts` and Node server in `frontend/src/mocks/server.ts`; start worker in `frontend/src/main.tsx` when `import.meta.env.DEV`
- [ ] T018 [P] Add anti-FOCT inline `<script>` to `frontend/index.html` reading `localStorage.getItem('theme')` and adding `dark` class to `<html>` before bundle loads
- [ ] T019 Create `AppLayout` component in `frontend/src/app/AppLayout.tsx`: persistent left sidebar with `Home`, `New Project`, `Projects`, `Settings`, `About` nav items (Lucide icons + labels); collapses to icon-only below 1024 px via `useMediaQuery`
- [ ] T020 Create `AuthGuard` component in `frontend/src/app/AuthGuard.tsx`: reads `authStore.isAuthenticated`; redirects to `/login` if false; stores intended destination in location state
- [ ] T021 Create router in `frontend/src/app/router.tsx` using `createBrowserRouter`: public route `/login`, protected routes `/` (Home), `/projects/new` (wizard), `/projects` (list), `/settings`, `/about` — all wrapped in `AppLayout` + `AuthGuard`; all page imports are `React.lazy()`
- [ ] T022 Create `useMediaQuery(query: string): boolean` hook in `frontend/src/hooks/useMediaQuery.ts`; create `useTheme()` hook in `frontend/src/hooks/useTheme.ts` (reads/writes `themeStore`)
- [ ] T023 Create `ErrorBoundary` component in `frontend/src/components/ErrorBoundary.tsx` conforming to Contract 5: shows title, message, optional retry button, always-present home button
- [ ] T024 Implement `LoginPage` in `frontend/src/features/auth/LoginPage.tsx` with React Hook Form + Zod; create `authService.ts` calling `POST /auth/login`; create `useLogin` mutation hook in `frontend/src/features/auth/hooks/useLogin.ts` — on success stores token via `authStore.setToken` and redirects to intended destination

**Checkpoint**: App shell renders, `/login` route works end-to-end with MSW, authenticated navigation works, dark mode toggles without flash

---

## Phase 3: User Story 1 — Upload and Transform a Document (Priority: P1) 🎯 MVP

**Goal**: Users can upload a `.docx` file, work through all five wizard steps, and download the rendered output.

**Independent Test**: Upload any `.docx`, accept all defaults, click through to Step 5, wait for "Finished", click Download. Verify the file saves to disk. No other user story required.

### Implementation for User Story 1

- [ ] T025 [US1] Create `UploadArea` component in `frontend/src/components/UploadArea.tsx` conforming to Contract 3: drag-and-drop + click-to-browse; validates `accept` (default `.docx`) and `maxSizeBytes` (default 50 MB) client-side before any network call; calls `onError` with inline message on rejection
- [ ] T026 [P] [US1] Create `WizardNav` step indicator in `frontend/src/components/WizardNav.tsx`: shows 5 numbered steps with active/complete/pending states, Back/Next buttons, disabled states
- [ ] T027 [P] [US1] Create `documentsService.ts` in `frontend/src/features/wizard/services/documentsService.ts`: `uploadDocument(file: File): Promise<UploadedDocument>` (`POST /documents/upload`, multipart), `analyseDocument(docId: string): Promise<DocumentAnalysis>` (`POST /documents/{id}/analyse`)
- [ ] T028 [P] [US1] Create `jobsService.ts` in `frontend/src/features/wizard/services/jobsService.ts`: `submitJob(req: JobSubmitRequest): Promise<JobSubmitResponse>`, `getJob(id: string): Promise<ParsedJob>` (calls `parseJob()`), `getEstimate(req): Promise<JobEstimate>`, `downloadJob(jobId: string, fmt: string): void` (triggers browser download via Blob URL)
- [ ] T029 [US1] Create wizard Zustand store in `frontend/src/features/wizard/wizardStore.ts` conforming to Contract 1: full `WizardDraft` state, all actions (`goNext`, `goBack`, `goToStep`, `setDocument`, `setAiConfig`, `setPublicationConfig`, `applyPreset`, `setEstimate`, `setActiveJob`, `reset`); persist entire draft to `sessionStorage` key `"wizard-draft"`; export `useWizardStore`
- [ ] T030 [P] [US1] Create built-in preset data constants in `frontend/src/features/wizard/presets.ts`: 7 presets (`travel-guide`, `book`, `magazine`, `academic-paper`, `annual-report`, `corporate-report`, `newsletter`) each with `id`, `name`, `description`, and `config: Partial<WizardDraft>`
- [ ] T031 [P] [US1] Create theme metadata constants in `frontend/src/features/wizard/themeMetadata.ts`: `THEME_METADATA: Record<string, { name: string; description: string }>` for all known theme IDs (`minimal`, `dk_eyewitness`, `lonely_planet`, `national_geographic`, `corporate`)
- [ ] T032 [US1] Create `useUploadDocument` mutation hook in `frontend/src/features/wizard/services/hooks/useUploadDocument.ts`: calls `documentsService.uploadDocument`, on success dispatches `wizardStore.setDocument` with result and initial null analysis
- [ ] T033 [P] [US1] Create `useAnalyseDocument` query hook in `frontend/src/features/wizard/services/hooks/useAnalyseDocument.ts`: enabled only when `docId` is non-null; on success dispatches `wizardStore.setDocument` with analysis result
- [ ] T034 [US1] Create `useSubmitJob` mutation hook in `frontend/src/features/wizard/services/hooks/useSubmitJob.ts`: builds `JobSubmitRequest` from wizard draft; on success dispatches `wizardStore.setActiveJob`; invalidates `projects` query
- [ ] T035 [P] [US1] Create `useEstimate` query hook in `frontend/src/features/wizard/services/hooks/useEstimate.ts`: calls `POST /jobs/estimate`; enabled when `docId` and `template` are available; on success dispatches `wizardStore.setEstimate`
- [ ] T036 [US1] Create `useJob` polling query hook in `frontend/src/features/wizard/services/hooks/useJob.ts`: `refetchInterval` stops when status is `COMPLETED`, `FAILED`, or `CANCELLED`; tracks consecutive polling failures in ref; exposes `connectionLost: boolean` (true after 3 failures), resets on success
- [ ] T037 [US1] Implement `Step1Upload` in `frontend/src/features/wizard/steps/Step1Upload.tsx`: renders `UploadArea`; on file accepted calls `useUploadDocument` then `useAnalyseDocument`; shows document metadata panel (filename, pages, headings, tables, image placeholders, estimated complexity) once analysis arrives; skeleton while loading
- [ ] T038 [US1] Implement `Step2AiConfig` in `frontend/src/features/wizard/steps/Step2AiConfig.tsx`: AI provider (read-only: OpenAI), AI model Select (GPT-5.6 / GPT-5.6-mini / GPT-5.6-sol / GPT-5.5), quality Radio (Fast / Balanced / Maximum), creativity Slider 1–10 with live description text; all fields backed by `wizardStore.setAiConfig`
- [ ] T039 [P] [US1] Create `PresetSelector` component in `frontend/src/components/PresetSelector.tsx` conforming to Contract 3: renders preset cards in a grid; calls `onChange(presetId)` on click; shows active preset highlighted
- [ ] T040 [P] [US1] Create `ThemeGallery` component in `frontend/src/components/ThemeGallery.tsx` conforming to Contract 3: fetches themes via `useThemes()`; renders each with preview image (static from `public/theme-previews/`) or colour swatch fallback; overlays name and description from `THEME_METADATA`; calls `onChange(themeId)` on selection
- [ ] T041 [P] [US1] Create `ColourPicker` component in `frontend/src/components/ColourPicker.tsx`: shown only when `colourPalette === 'custom'` in the wizard draft; native `<input type="color">` bound to `wizardStore.draft.customColour`
- [ ] T042 [US1] Implement `Step3PublicationConfig` in `frontend/src/features/wizard/steps/Step3PublicationConfig.tsx`: renders `PresetSelector` and `ThemeGallery`; all Step 3 fields from `WizardDraft` (theme, output formats, language, image policy, image sources, image density, layout density, typography, colour palette + `ColourPicker`, sidebar style, cover page, ToC, headers/footers, validation level, AI explainability, offline mode); Advanced Settings collapsible section (collapsed by default) with: prompt version, theme version, parallel downloads, retry count, timeout, cache location, cache size, max AI requests; all fields backed by `wizardStore.setPublicationConfig`; applying a preset calls `wizardStore.applyPreset`
- [ ] T043 [P] [US1] Create `CostCard` in `frontend/src/components/CostCard.tsx` conforming to Contract 3 and `StatisticsCard` in `frontend/src/components/StatisticsCard.tsx` conforming to Contract 3
- [ ] T044 [US1] Implement `Step4Preview` in `frontend/src/features/wizard/steps/Step4Preview.tsx`: calls `useEstimate`; renders `CostCard` and `StatisticsCard` grid (estimated rendering time, AI cost, AI requests, downloaded images, page count, photographs, captions, appendix, cover page, ToC, warnings list, validation summary, licence summary); skeleton screen while loading; "Generate" button triggers `useSubmitJob` and advances to Step 5
- [ ] T045 [P] [US1] Create `ProgressTimeline` component in `frontend/src/components/ProgressTimeline.tsx` conforming to Contract 3: renders each `ProgressStage` with icon, label, status indicator (pending/active/complete/error), progress bar (active only), and elapsed time
- [ ] T046 [US1] Implement `Step5Rendering` in `frontend/src/features/wizard/steps/Step5Rendering.tsx`: calls `useJob(activeJobId, { pollingInterval: 3000 })`; maps `RenderStage` values to `ProgressStage` props for `ProgressTimeline`; shows `connectionLost` banner ("Connection lost — retrying…") when hook reports 3+ consecutive failures, auto-dismisses on reconnect; on `COMPLETED` shows Download button calling `jobsService.downloadJob`; on `FAILED` shows error message with "Back to settings" link; on `CANCELLED` shows cancellation message
- [ ] T047 [US1] Implement `NewProjectWizard` root in `frontend/src/features/wizard/NewProjectWizard.tsx`: on mount checks `sessionStorage` for saved draft; if draft exists, shows dialog "You have an unfinished project — continue or start fresh?" — "Continue" restores draft, "Start fresh" calls `wizardStore.reset()`; renders current step component based on `wizardStore.step`; wraps each step in `ErrorBoundary`
- [ ] T048 [US1] Implement `HomePage` in `frontend/src/features/home/HomePage.tsx`: renders `UploadArea` as primary CTA (on file accepted navigates to `/projects/new` and calls `useUploadDocument`); shows recent projects section (calls `useProjects({ limit: 3 })`) with skeleton; empty state when no projects; quick action buttons ("New Project", "Browse Projects")

**Checkpoint**: Full wizard end-to-end works with MSW: upload → metadata → AI config → publication config (presets apply) → preview (estimate shows) → submit → polling progress → download. Draft restored on page refresh.

---

## Phase 4: User Story 2 — Manage Existing Publications (Priority: P2)

**Goal**: Users can list, duplicate, download, and delete past projects.

**Independent Test**: Pre-seed MSW with two `COMPLETED` projects. Navigate to `/projects`. Verify all four card actions (Open, Duplicate, Download, Delete) work. Verify empty-state renders when no projects exist. No wizard dependency required.

### Implementation for User Story 2

- [ ] T049 [US2] Create `projectsService.ts` in `frontend/src/features/projects/services/projectsService.ts`: `getProjects(params?: { offset?: number; limit?: number }): Promise<ParsedProject[]>` (calls `parseProject()` on each), `getProject(id): Promise<ParsedProject>`, `duplicateProject(id): Promise<JobSubmitResponse>` (`POST /projects/{id}/duplicate`), `deleteProject(id): Promise<void>`
- [ ] T050 [P] [US2] Create `useProjects` query hook in `frontend/src/features/projects/services/hooks/useProjects.ts`: accepts `{ offset, limit }` params; query key includes both; returns `ParsedProject[]`
- [ ] T051 [P] [US2] Create `useProject` query hook in `frontend/src/features/projects/services/hooks/useProject.ts`
- [ ] T052 [P] [US2] Create `useDuplicateProject` mutation hook in `frontend/src/features/projects/services/hooks/useDuplicateProject.ts`: on success invalidates `projects` query; shows button spinner while pending
- [ ] T053 [P] [US2] Create `useDeleteProject` mutation hook in `frontend/src/features/projects/services/hooks/useDeleteProject.ts`: on success invalidates `projects` query; requires confirmation dialog before firing
- [ ] T054 [US2] Implement `ProjectCard` in `frontend/src/features/projects/ProjectCard.tsx`: displays name, creation date, template, language, AI model, status badge (colour-coded by `JobStatus`), output format chips; action buttons: Open (navigates to wizard Step 5 with that job), Duplicate (`useDuplicateProject` with spinner), Download (calls `jobsService.downloadJob`, shown only for `COMPLETED`), Delete (opens confirm dialog, then `useDeleteProject` with spinner); skeleton variant when `loading` prop is true
- [ ] T055 [US2] Implement `ProjectsPage` in `frontend/src/features/projects/ProjectsPage.tsx`: calls `useProjects({ offset: (page-1)*20, limit: 20 })`; renders grid of `ProjectCard`; skeleton screens (20 placeholder cards) while loading; empty state illustration + "Create Publication" CTA when no projects; numbered pagination controls at bottom (shows when total > 20)

**Checkpoint**: Projects page renders, all 4 card actions work with MSW, pagination navigates between pages, empty state shows when no data.

---

## Phase 5: User Story 3 — Configure Global Settings (Priority: P3)

**Goal**: Users can toggle dark/light mode (persisted), set default language/format/template, and store their OpenAI API key.

**Independent Test**: Open `/settings`, toggle dark mode, reload page — dark mode persists. No wizard or projects dependency required.

### Implementation for User Story 3

- [ ] T056 [US3] Create `settingsStore.ts` in `frontend/src/features/settings/settingsStore.ts` conforming to Contract 6: `AppSettings` state with `DEFAULT_SETTINGS`; `set(partial)` merges updates; `setApiKey` / `getApiKey` for sensitive field; `reset()`; persists to `localStorage` key `"settings"`; `theme` field syncs with `themeStore.setTheme` on change
- [ ] T057 [US3] Implement `SettingsPage` in `frontend/src/features/settings/SettingsPage.tsx`: Dark/Light mode Switch (reads/writes `themeStore`); default language Select; default output format Select; default template Select; OpenAI API key Input (type password, never logs value); Save button with inline spinner; all fields initialized from `settingsStore.get()`; on save calls `settingsStore.set()`; shows success toast on save

**Checkpoint**: Dark mode toggle switches theme immediately and persists on reload. Settings saved values pre-populate wizard Step 2 and Step 3 defaults.

---

## Phase 6: User Story 4 — Learn About the Application (Priority: P4)

**Goal**: Users can read the app version, documentation, licences, and find the GitHub repository.

**Independent Test**: Navigate to `/about`. Verify version number, docs link, contributor list, licence details, and GitHub URL are present. Click GitHub link — opens in new tab. No backend dependency.

### Implementation for User Story 4

- [ ] T058 [US4] Implement `AboutPage` in `frontend/src/features/about/AboutPage.tsx`: calls `useHealth()` to display live version number (fallback to build-time `VITE_APP_VERSION`); renders documentation link, contributor list, licence text (MIT), GitHub repository link (opens in `_blank` with `rel="noopener noreferrer"`); fully static when backend is unreachable

**Checkpoint**: About page renders all required information with no runtime errors regardless of backend availability.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories; can be done in parallel by separate contributors once all user stories are complete.

- [ ] T059 Audit and implement skeleton screens across all loading states: page-level (Home, Projects), list-level (project cards), inline (step transitions); ensure every `useQuery` pending state shows a content-shaped placeholder rather than a spinner, in all affected components
- [ ] T060 [P] Add Framer Motion page transition animations in `frontend/src/app/AppLayout.tsx` (fade on route change) and wizard step transitions in `frontend/src/features/wizard/NewProjectWizard.tsx` (slide direction matches forward/back navigation)
- [ ] T061 [P] WCAG AA audit across all components: add `aria-label` to all icon-only buttons, ensure all form fields have associated `<label>`, verify visible focus rings (Tailwind `focus-visible:ring`), test Tab/Shift-Tab/Enter/Space/Arrow navigation through wizard and project card actions
- [ ] T062 [P] Write Vitest unit tests in `frontend/tests/unit/`: `authStore.test.ts` (setToken, logout, localStorage persistence), `themeStore.test.ts` (setTheme, class toggle), `wizardStore.test.ts` (applyPreset, reset, sessionStorage round-trip), `utils.test.ts` (parseJob, parseProject, formatBytes)
- [ ] T063 [P] Write RTL component tests in `frontend/tests/component/`: `UploadArea.test.tsx` (rejects PDF, rejects >50 MB, accepts .docx, calls onFile), `ProgressTimeline.test.tsx` (renders all stages, active stage shows progress bar), `WizardNav.test.tsx` (back hidden on step 1, all steps shown)
- [ ] T064 Write Playwright E2E test for full wizard happy path in `frontend/tests/e2e/wizard.spec.ts` (Quickstart Scenario 3): upload .docx → step through all 5 steps → confirm "Finished" → download
- [ ] T065 [P] Write Playwright E2E tests for Projects page actions in `frontend/tests/e2e/projects.spec.ts` (Quickstart Scenario 4): duplicate, download, delete; verify empty state
- [ ] T066 [P] Write Playwright E2E tests for Settings in `frontend/tests/e2e/settings.spec.ts` (Quickstart Scenario 5): toggle dark mode, reload, verify persisted
- [ ] T067 [P] Verify wizard defaults use settings values: open wizard after saving non-default language in Settings; confirm Step 3 language field pre-selects that value from `settingsStore`

**Checkpoint**: All unit and component tests pass (`pnpm test`), E2E tests pass against running backend (`pnpm test:e2e`), no WCAG AA violations in axe-core scan, dark/light mode has no flash of wrong theme on cold load

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)         → no dependencies, start immediately
Phase 2 (Foundational)  → requires Phase 1 complete, BLOCKS all user stories
Phase 3 (US1 — Wizard)  → requires Phase 2 complete
Phase 4 (US2 — Projects)→ requires Phase 2 complete; independent of Phase 3
Phase 5 (US3 — Settings)→ requires Phase 2 complete; independent of Phases 3–4
Phase 6 (US4 — About)   → requires Phase 2 complete; independent of Phases 3–5
Phase 7 (Polish)        → requires all user story phases complete
```

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories. Requires foundational API client, stores, types, auth, app shell.
- **US2 (P2)**: No dependency on US1. Requires foundational layer only. `useProjects` is also called by `HomePage` (US1), so US2 services may be started in parallel with US1 once Phase 2 is done.
- **US3 (P3)**: No dependency on other stories. `settingsStore` values feed into US1 wizard defaults — implement US3 first if you want pre-populated wizard defaults, but it is not blocking.
- **US4 (P4)**: Fully independent. Requires only `useHealth` hook which is part of the foundational MSW setup.

### Within Each User Story

- Services (`documentsService`, `jobsService`, `projectsService`) before their hooks
- Hooks before the step/page components that consume them
- Store (`wizardStore`) before any step component
- Shared UI components (`UploadArea`, `ProgressTimeline`, etc.) before the step that uses them
- `NewProjectWizard` root after all 5 step components

### Parallel Opportunities

Tasks marked `[P]` within the same phase touch different files and can be worked simultaneously:

```bash
# Phase 2 — can start all of these at once after T009:
T010  frontend/src/types/ui.ts
T011  frontend/src/lib/api.ts
T012  frontend/src/lib/queryClient.ts
T013  frontend/src/lib/utils.ts
T014  frontend/src/stores/authStore.ts
T015  frontend/src/stores/themeStore.ts
T016  frontend/src/mocks/handlers.ts
T017  frontend/src/mocks/browser.ts + server.ts

# Phase 3 — once wizard store and services are done:
T030  frontend/src/features/wizard/presets.ts
T031  frontend/src/features/wizard/themeMetadata.ts
T039  frontend/src/components/PresetSelector.tsx
T040  frontend/src/components/ThemeGallery.tsx
T041  frontend/src/components/ColourPicker.tsx
T043  frontend/src/components/CostCard.tsx + StatisticsCard.tsx
T045  frontend/src/components/ProgressTimeline.tsx

# Phase 4 — once projectsService (T049) is done:
T050  hooks/useProjects.ts
T051  hooks/useProject.ts
T052  hooks/useDuplicateProject.ts
T053  hooks/useDeleteProject.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — **do not skip, it blocks everything**
3. Complete Phase 3: User Story 1 (T025 → T048)
4. **STOP and VALIDATE**: Run full wizard end-to-end with MSW; test draft persistence; test file size rejection
5. Deploy/demo MVP — the product is already functional

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 → US1: Upload + Transform wizard → **MVP**
3. Phase 4 → US2: Projects list → returning users can manage work
4. Phase 5 → US3: Settings → power user personalisation
5. Phase 6 → US4: About → open-source compliance
6. Phase 7 → Polish: animations, accessibility, tests

Each phase adds user-visible value without breaking any previous phase.

### Parallel Team Strategy

With multiple developers (after Phase 2 completes):

- Developer A: Phase 3 (US1 wizard) — most complex, longest path
- Developer B: Phase 4 (US2 projects) + Phase 5 (US3 settings)
- Developer C: Phase 6 (US4 about) + Phase 7 polish/tests

---

## Summary

| Phase | Tasks | User Story | Parallel Tasks |
|-------|-------|------------|----------------|
| 1 — Setup | T001–T008 | — | 7 of 8 |
| 2 — Foundational | T009–T024 | — | 10 of 16 |
| 3 — Wizard | T025–T048 | US1 (P1) | 11 of 24 |
| 4 — Projects | T049–T055 | US2 (P2) | 4 of 7 |
| 5 — Settings | T056–T057 | US3 (P3) | 0 of 2 |
| 6 — About | T058 | US4 (P4) | 0 of 1 |
| 7 — Polish | T059–T067 | — | 6 of 9 |
| **Total** | **67** | | **38 parallelizable** |

**MVP scope**: Phases 1–3 (48 tasks) → fully functional Upload + Transform wizard.

**Independent test for each story**:
- US1: Upload any `.docx`, accept defaults, complete wizard, download — no other story required
- US2: Open `/projects` with MSW-seeded data, exercise all 4 card actions — no wizard required
- US3: Toggle dark mode at `/settings`, reload, verify persisted — no backend required
- US4: Open `/about`, verify all static content present — no backend required

**Suggested next command**: `/speckit-implement`
