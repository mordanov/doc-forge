# Quickstart: DocForge Frontend Application

**Feature**: `002-frontend-app`  
**Date**: 2026-07-27

Integration scenarios for end-to-end testing and developer onboarding.

---

## Prerequisites

- DocForge backend running on `http://localhost:8000` (run `docforge server` or `uvicorn docforge.server.app:app`)
- Backend initialised with `docforge init` (creates the admin user)
- Node.js 20+, pnpm 9+

---

## Scenario 1 — First-time Setup

```bash
# 1. Enter the frontend directory
cd frontend

# 2. Install dependencies
pnpm install

# 3. Configure environment
cp .env.example .env
# Edit .env: set VITE_API_URL=http://localhost:8000

# 4. Start dev server
pnpm dev
# → Application running at http://localhost:5173
```

Expected: Home page loads, shows "No recent projects", displays the upload area.

---

## Scenario 2 — Login Flow

1. Navigate to `http://localhost:5173` — should redirect to `/login`
2. Enter credentials: username `admin`, password from `docforge init` output (default: `admin`)
3. Click "Sign in"

Expected:
- JWT token stored in `localStorage` under the `auth` key
- Redirect to Home page
- Navigation bar shows username

---

## Scenario 3 — Full Wizard Walk-through (Happy Path)

Requires: a `.docx` test file. A minimal one-page document works.

1. From Home page, drag-and-drop a `.docx` file onto the upload area
2. **Step 1**: Verify document metadata panel shows filename, pages, headings, tables, placeholders, estimated complexity. Click "Next".
3. **Step 2**: Leave AI model as default. Set creativity to 7. Click "Next".
4. **Step 3**: Select "Travel Guide" preset — verify all fields update. Click "Next".
5. **Step 4**: Preview dashboard loads with estimated time, AI cost, warnings. Click "Generate".
6. **Step 5**: Progress timeline advances through stages. Wait for "Finished".
7. Click "Download" — `.docx` file downloads.

Expected: Completed project appears on Projects page.

---

## Scenario 4 — Projects List Actions

Requires: at least one completed project from Scenario 3.

1. Navigate to `/projects`
2. Verify each card shows: name, date, template, language, AI model, status, output format
3. Click "Duplicate" on a card — verify new card appears in QUEUED status
4. Click "Download" on a completed card — file downloads
5. Click "Delete" on any card, confirm in dialog — card removed from list

---

## Scenario 5 — Dark Mode Toggle

1. Open Settings (`/settings`)
2. Toggle "Dark Mode"
3. Verify entire UI switches to dark colour scheme immediately
4. Reload page — verify dark mode persists

---

## Scenario 6 — Error Handling

1. Stop the backend (`Ctrl+C` on `docforge server`)
2. Reload the frontend
3. Attempt login

Expected:
- Login form shows a user-friendly error message (not a raw stack trace)
- Application does not crash

4. Restart backend, log in again — application recovers normally

---

## Scenario 7 — Upload Validation

1. Attempt to drag a `.pdf` file onto the upload area
Expected: Error message "Only .docx files are accepted" — file is rejected before upload.

2. Attempt to drag a file larger than 50 MB
Expected: Error message about file size limit — rejected client-side before upload attempt.

---

## Scenario 8 — Keyboard Navigation

1. Open the New Project wizard
2. Navigate all five steps using only Tab, Shift+Tab, Enter, Space, and arrow keys
3. Confirm all interactive elements are reachable and operable without a mouse

Expected: No step requires a pointer device.

---

## API Mock Setup (for tests without a backend)

Using Mock Service Worker:

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/auth/login', () =>
    HttpResponse.json({ access_token: 'mock-token', token_type: 'bearer' })
  ),
  http.get('/system/health', () =>
    HttpResponse.json({ status: 'ok', version: '1.0.0' })
  ),
  http.get('/system/themes', () =>
    HttpResponse.json([
      { id: 'minimal', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: false },
    ])
  ),
  // ... add more handlers for each tested flow
]
```

```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'
export const worker = setupWorker(...handlers)
```

Start in development: `worker.start()` in `main.tsx` when `import.meta.env.DEV`.

---

## Build & Production

```bash
pnpm build
# Output: dist/

# Serve production build locally
pnpm preview
# → http://localhost:4173
```

The production build is a static SPA. Deploy `dist/` to any static host or serve it from the backend's static file mount.
