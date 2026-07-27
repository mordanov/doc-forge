# Feature Specification: DocForge Frontend Application

**Feature Branch**: `002-frontend-app`  
**Created**: 2026-07-27  
**Status**: Draft  
**Input**: User description: "@documentation/frontend-specification.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Upload and Transform a Document (Priority: P1)

A user visits DocForge, drags a Word document onto the home page upload area, works through the New Project wizard, and downloads the finished publication. This is the end-to-end core journey.

**Why this priority**: The wizard is the product. Every other feature supports or extends it. No other story delivers value without this one.

**Independent Test**: Can be fully tested by uploading any .docx file, clicking through all five wizard steps with default settings, and confirming a downloadable output is produced.

**Acceptance Scenarios**:

1. **Given** a user is on the Home page, **When** they drag and drop a .docx file onto the upload area, **Then** the wizard opens at Step 1 with filename, page count, heading count, table count, image count, and estimated complexity displayed.
2. **Given** the user is on Step 2 (AI Configuration), **When** they select a model and adjust creativity, **Then** the description beneath the creativity slider updates to reflect the current value.
3. **Given** the user is on Step 3 (Publication Configuration), **When** they select a preset (e.g., "Travel Guide"), **Then** every configuration option updates automatically and the user can still modify individual settings.
4. **Given** the user is on Step 4 (Preview), **When** the page loads, **Then** estimated rendering time, AI cost, AI requests, image count, page count, warnings, validation summary, and licence summary are all visible.
5. **Given** the user is on Step 5 (Rendering), **When** rendering runs, **Then** each stage (Uploading → Finished) shows its icon, a progress indicator, and elapsed time, advancing in real time.
6. **Given** rendering is complete, **When** the user clicks Download, **Then** the output file is saved to their device in the format they selected.

---

### User Story 2 — Manage Existing Publications (Priority: P2)

A user navigates to the Projects page to review, re-download, duplicate, or delete previously generated publications.

**Why this priority**: Returning users need to access past work without starting from scratch. Duplicate enables quick iteration on settings.

**Independent Test**: Can be tested by pre-seeding the database with two projects and verifying all four actions (Open, Duplicate, Download, Delete) work correctly from the Projects page.

**Acceptance Scenarios**:

1. **Given** the user has previous projects, **When** they open the Projects page, **Then** each project card shows name, creation date, template, language, AI model, rendering status, and available output formats.
2. **Given** a project with status COMPLETED, **When** the user clicks Download, **Then** the output file downloads without navigating away.
3. **Given** any project, **When** the user clicks Duplicate, **Then** a new job is queued and the Projects list refreshes to show the duplicate in QUEUED status.
4. **Given** any project, **When** the user clicks Delete and confirms, **Then** the card is removed from the list and cannot be recovered.
5. **Given** no projects exist, **When** the user opens the Projects page, **Then** an empty-state illustration with a "Create Publication" CTA is shown.

---

### User Story 3 — Configure Global Settings (Priority: P3)

A user visits the Settings page to adjust application-wide preferences such as theme (dark/light), default AI provider, default output format, and stored API credentials.

**Why this priority**: Settings personalise the experience but the product functions with defaults. Useful for power users.

**Independent Test**: Can be tested independently by changing dark/light mode and confirming it persists across page reloads, with no dependency on the wizard or projects list.

**Acceptance Scenarios**:

1. **Given** the user opens Settings, **When** they toggle Dark/Light mode, **Then** the entire interface switches theme immediately and the preference is retained on next visit.
2. **Given** the user changes a default (e.g., default language), **When** they later open the New Project wizard, **Then** that default is pre-selected on Step 3.
3. **Given** the user enters an OpenAI API key in Settings, **When** they save, **Then** the key is stored and used for subsequent jobs without re-entry.

---

### User Story 4 — Learn About the Application (Priority: P4)

A user visits the About page to find the application version, read documentation, review licences, and find the GitHub repository.

**Why this priority**: Informational only. Does not affect core functionality but required for open-source compliance and user trust.

**Independent Test**: Fully testable by verifying the About page renders with version number, documentation link, licence text, and GitHub URL — with no backend dependency.

**Acceptance Scenarios**:

1. **Given** the user opens the About page, **When** it renders, **Then** the application version, documentation link, contributor list, licence details, and GitHub repository link are all visible.
2. **Given** the user clicks the GitHub link, **When** they click, **Then** it opens in a new tab.

---

### Edge Cases

- What happens when a file larger than 50 MB is dropped onto the upload area? → Rejected client-side before upload with an inline error message in the upload area; no network request is made.
- How does the wizard behave if the backend is unreachable during Step 5? → Silent retry; "Connection lost — retrying…" banner after 3 consecutive failures, auto-dismissed on reconnect.
- What happens if the user closes the browser during rendering? → Job continues on the backend; on return the user sees the job status on the Projects page (or resumes polling if they navigate back to the wizard).
- How does the Projects page behave with 100+ projects? → Paginated, 20 per page.
- What happens if an AI API key is invalid when a job starts? → The job transitions to FAILED on the backend; Step 5 displays the error message from the job record with a "Back to settings" action link.
- How does the creativity slider behave when a preset changes it to a value outside the user's last manual input? → Preset value is applied and the slider moves to it; subsequent manual adjustment overrides the preset value without re-applying the preset.
- What is shown if the backend returns a theme list with no preview images? → A placeholder colour swatch using the theme's primary palette colour is shown in place of the preview image.

---

## Clarifications

### Session 2026-07-27

- Q: What is the primary navigation pattern? → A: Left sidebar with icons and labels, always visible, collapses to icon-only on narrow viewports.
- Q: How does the Projects page handle 100+ projects? → A: Pagination — fixed page size of 20, numbered page controls at the bottom.
- Q: What happens to wizard progress on page refresh or accidental navigation? → A: Draft is restored with a confirmation prompt: "You have an unfinished project — continue or start fresh?"
- Q: What does Step 5 show when the backend becomes unreachable mid-render? → A: Retry silently; surface a "Connection lost — retrying…" banner after 3 consecutive polling failures.
- Q: What loading pattern is used across the application? → A: Skeleton screens for page and list loads; button-level spinner for inline actions (delete, duplicate, submit).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST provide a five-page structure: Home, New Project, Projects, Settings, About, accessible via a persistent left sidebar. The sidebar MUST display icons and labels when space permits and collapse to icon-only on viewports below 1024 px wide.
- **FR-002**: The Home page MUST display recent projects, quick actions, and a drag-and-drop upload area with a "Create Publication" primary CTA.
- **FR-003**: The New Project wizard MUST guide users through exactly five sequential steps: Upload, AI Configuration, Publication Configuration, Preview, Generate. Wizard progress MUST be persisted across page reloads; on return, the user MUST be shown a prompt: "You have an unfinished project — continue or start fresh?" Choosing "start fresh" discards the saved draft.
- **FR-004**: Step 1 MUST display document metadata (filename, page count, heading count, table count, image count, estimated complexity) after upload.
- **FR-005**: Step 2 MUST allow selection of AI provider (OpenAI), AI model (GPT-5.6, GPT-5.6-mini, GPT-5.6-sol, GPT-5.5), AI quality (Fast / Balanced / Maximum Quality), and a creativity slider (1–10) with a live description.
- **FR-006**: Step 3 MUST allow configuration of theme, output format, language, image policy, image sources, image density, layout density, typography, colour palette, sidebar style, cover page, table of contents, headers and footers, validation level, AI explainability, and offline mode toggle.
- **FR-007**: Step 3 MUST provide built-in presets (Travel Guide, Book, Magazine, Academic Paper, Annual Report, Corporate Report, Newsletter) that configure all options at once while remaining individually overridable.
- **FR-008**: Step 3 MUST include an "Advanced Settings" section (collapsed by default) containing prompt version, theme version, parallel downloads, retry count, timeout, cache location, cache size, and maximum AI requests.
- **FR-009**: Step 4 MUST display a preview dashboard with estimated rendering time, AI cost, AI requests, downloaded images, page count, photographs, captions, appendix, cover page, table of contents, warnings, validation summary, and licence summary.
- **FR-010**: Step 5 MUST display a real-time progress timeline covering: Uploading, Analysing, AI Processing, Searching Images, Downloading Images, Rendering, Validation, Export, Finished — each with icon, progress indicator, and elapsed time. When backend polling fails, the UI MUST retry silently and display a "Connection lost — retrying…" banner only after 3 consecutive failures; the banner MUST dismiss automatically when connectivity is restored.
- **FR-011**: The Projects page MUST list all past publications as cards, each showing name, creation date, template, language, AI model, rendering status, and output formats, with Open, Duplicate, Download, and Delete actions. The list MUST be paginated with a fixed page size of 20 and numbered page controls; projects are ordered by creation date descending.
- **FR-012**: Every interactive control MUST include a tooltip and a short explanatory label.
- **FR-017**: Page and list loading states MUST use skeleton screens (content-shaped placeholders). Inline actions (delete, duplicate, form submit) MUST show a button-level spinner and disable the control while in progress.
- **FR-013**: The application MUST support Dark Mode and Light Mode, switchable by the user and persisted across sessions.
- **FR-014**: The application MUST comply with WCAG AA: keyboard navigation, visible focus indicators, and screen reader support.
- **FR-015**: The colour palette option MUST reveal a colour picker when "Custom" is selected.
- **FR-016**: The theme selection MUST display a preview image and short description alongside each option.

### Key Entities

- **Project**: A completed publication. Attributes: id, name, created date, template, language, AI model, rendering status, output format(s), input filename.
- **Job**: A rendering run. Attributes: id, project association, status (QUEUED / RUNNING / COMPLETED / FAILED / CANCELLED), stage, progress percentage, elapsed time, warnings, error message.
- **Document**: An uploaded .docx file. Attributes: id, filename, upload size, metadata (page count, heading count, table count, image count, estimated complexity).
- **Preset**: A named configuration bundle. Attributes: name, description, all Step 3 field values.
- **Theme**: A visual template. Attributes: id, display name, preview image URL, description.
- **AppSettings**: User preferences stored locally. Attributes: colour scheme (dark/light), default language, default output format, OpenAI API key (encrypted).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time user can upload a document and start rendering within five minutes of opening the application, without reading any documentation.
- **SC-002**: The New Project wizard can be completed end-to-end in under three minutes using default settings.
- **SC-003**: All five pages load and become interactive in under two seconds on a standard broadband connection.
- **SC-004**: The application is fully navigable by keyboard alone, with no interaction requiring a pointing device.
- **SC-005**: Dark Mode and Light Mode are visually consistent — no controls have illegible contrast in either mode.
- **SC-006**: The Projects page remains responsive and usable with at least 50 project cards displayed simultaneously.
- **SC-007**: Every form field provides validation feedback within one second of user input.
- **SC-008**: The rendering progress timeline updates within three seconds of each stage transition on the backend.

---

## Assumptions

- The backend REST API described in the DocForge backend specification is available and stable; the frontend does not implement any rendering logic.
- Users access the application on desktop or laptop browsers (13"+ screen); mobile is a stretch goal, not a v1 requirement.
- Authentication is single-user (admin only) as defined by the backend; multi-user login flows are out of scope.
- The OpenAI API key may be provided either in the backend `.env` or stored in the frontend Settings page; both paths must work.
- Theme preview images are served by the backend or bundled as static assets; the frontend does not generate them.
- The application runs as a single-page application served from the same host as the backend, enabling relative API URLs without CORS configuration.
- PDF export capability on the backend may not be available in v1; the frontend should handle gracefully the case where only DOCX output is returned.
- Browser local storage (or equivalent) is used to persist dark/light mode preference and default settings; no server-side user profile storage is required.
