# UI Contracts: DocForge Frontend Application

**Feature**: `002-frontend-app`
**Date**: 2026-07-27

These contracts define the interface between the UI layer and the data/API layer. They are the agreed boundaries for component development.

---

## Contract 1: Wizard State Machine

The wizard component MUST conform to this state interface. Any state persistence mechanism (Zustand, sessionStorage) MUST implement this contract.

```typescript
interface WizardContract {
  // Current step (1–5)
  step: WizardStep;
  draft: WizardDraft;

  // Navigation — goBack only valid for steps 2–3
  goNext(): void;
  goBack(): void;
  goToStep(step: WizardStep): void;

  // Data setters
  setDocument(doc: UploadedDocument, analysis: DocumentAnalysis): void;
  setAiConfig(config: AiConfig): void;
  setPublicationConfig(config: PublicationConfig): void;
  applyPreset(presetId: string): void;
  setEstimate(estimate: JobEstimate): void;
  setActiveJob(jobId: string): void;

  // Lifecycle
  reset(): void;   // clears draft and returns to step 1
}
```

---

## Contract 2: API Client Interface

All components MUST consume the backend through these TanStack Query hooks, never through raw Axios calls.

```typescript
// Auth
useLogin(): UseMutationResult<AuthToken, ApiError, LoginRequest>
useCurrentUser(): { isAuthenticated: boolean; token: string | null }

// Documents
useUploadDocument(): UseMutationResult<UploadedDocument, ApiError, File>
useAnalyseDocument(docId: string): UseQueryResult<DocumentAnalysis, ApiError>

// Jobs
useSubmitJob(): UseMutationResult<JobSubmitResponse, ApiError, JobSubmitRequest>
useJob(jobId: string, options?: { pollingInterval?: number }): UseQueryResult<ParsedJob, ApiError>
useEstimate(docId: string, template: string): UseQueryResult<JobEstimate, ApiError>
useDeleteJob(): UseMutationResult<void, ApiError, string>
useDownloadJob(jobId: string, fmt: string): { download(): void }

// Projects
useProjects(params?: { offset?: number; limit?: number }): UseQueryResult<ParsedProject[], ApiError>
useProject(id: string): UseQueryResult<ParsedProject, ApiError>
useDuplicateProject(): UseMutationResult<JobSubmitResponse, ApiError, string>
useDeleteProject(): UseMutationResult<void, ApiError, string>

// System
useHealth(): UseQueryResult<HealthCheck, ApiError>
useThemes(): UseQueryResult<Theme[], ApiError>
useProviders(): UseQueryResult<ProvidersStatus, ApiError>
```

**Polling contract**: `useJob` MUST accept a `pollingInterval` option. When provided, it polls until `status` reaches a terminal state (`COMPLETED`, `FAILED`, `CANCELLED`), then stops automatically.

---

## Contract 3: Shared Component Props

These props interfaces define the boundaries for shared reusable components.

### UploadArea

```typescript
interface UploadAreaProps {
  onFile(file: File): void;
  onError(message: string): void;
  accept?: string[];            // default: ['.docx']
  maxSizeBytes?: number;        // default: 50 * 1024 * 1024
  disabled?: boolean;
  children?: React.ReactNode;   // optional custom content
}
```

### ProgressTimeline

```typescript
interface ProgressTimelineProps {
  stages: ProgressStage[];
  currentStage: string;
}

interface ProgressStage {
  id: string;
  label: string;
  icon: LucideIcon;
  status: 'pending' | 'active' | 'complete' | 'error';
  progress?: number;          // 0–100, shown only when status === 'active'
  elapsedSeconds?: number;
}
```

### ThemeGallery

```typescript
interface ThemeGalleryProps {
  themes: Theme[];
  selected: string;
  onChange(themeId: string): void;
  disabled?: boolean;
}
```

### PresetSelector

```typescript
interface PresetSelectorProps {
  presets: Preset[];
  selected: string | null;
  onChange(presetId: string): void;
}
```

### CostCard

```typescript
interface CostCardProps {
  estimate: JobEstimate;
  loading?: boolean;
}
```

### StatisticsCard

```typescript
interface StatisticsCardProps {
  label: string;
  value: number | string;
  unit?: string;
  icon?: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
}
```

---

## Contract 4: Route Guards

The router MUST enforce these rules before rendering any protected route.

```typescript
interface RouteGuardContract {
  // Must be called on every route under AppLayout
  requiresAuth: true;

  // Redirect targets
  unauthenticatedRedirect: '/login';
  postLoginRedirect: '/';    // or the intended destination if stored

  // Exception routes (no auth required)
  publicRoutes: ['/login'];
}
```

---

## Contract 5: Error Boundaries

Every page and every major async boundary MUST be wrapped in an error boundary that conforms to this display contract.

```typescript
interface ErrorBoundaryContract {
  // What to show on caught error
  fallback: {
    title: string;           // e.g. "Something went wrong"
    message: string;         // human-readable, from error.message or ApiError.detail
    retryAction?: () => void; // shown as a "Try again" button if provided
    homeAction: () => void;   // always shown as "Go home"
  };
}
```

---

## Contract 6: Settings Persistence

The settings store MUST persist and hydrate using this contract, so components can depend on a consistent shape regardless of storage mechanism.

```typescript
interface SettingsPersistenceContract {
  // Read
  get(): AppSettings;

  // Write — merges partial updates
  set(partial: Partial<AppSettings>): void;

  // Sensitive field — never log, never include in error reports
  setApiKey(key: string | null): void;
  getApiKey(): string | null;

  // Reset all to defaults
  reset(): void;
}

const DEFAULT_SETTINGS: AppSettings = {
  theme: 'light',
  defaultLanguage: 'en',
  defaultOutputFormat: 'docx',
  defaultTemplate: 'minimal',
  openAiApiKey: null,
};
```
