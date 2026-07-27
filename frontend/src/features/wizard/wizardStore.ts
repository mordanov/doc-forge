import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { WizardDraft, WizardStep } from '@/types/ui'
import type { DocumentAnalysis, JobEstimate, UploadedDocument } from '@/types/api'
import { PRESETS } from './presets'

const DEFAULT_DRAFT: WizardDraft = {
  step: 1,
  documentId: null,
  filename: null,
  analysis: null,
  aiProvider: 'openai',
  aiModel: 'gpt-4o',
  aiQuality: 'balanced',
  creativity: 5,
  presetId: null,
  template: 'minimal',
  outputFormats: ['docx'],
  language: 'en',
  imagePolicy: 'auto',
  imageSources: ['pexels', 'unsplash'],
  imageDensity: 'balanced',
  layoutDensity: 'balanced',
  typography: 'serif',
  colourPalette: 'auto',
  customColour: null,
  sidebarStyle: 'none',
  coverPage: 'simple',
  tableOfContents: 'standard',
  headersFooters: 'standard',
  validationLevel: 'standard',
  aiExplainability: 'off',
  offlineMode: false,
  promptVersion: null,
  themeVersion: null,
  parallelDownloads: 3,
  retryCount: 3,
  timeout: 300,
  cacheLocation: null,
  cacheSize: null,
  maxAiRequests: null,
  estimate: null,
  activeJobId: null,
}

interface WizardState {
  draft: WizardDraft
  hasSavedDraft: boolean
  goNext: () => void
  goBack: () => void
  goToStep: (step: WizardStep) => void
  setDocument: (doc: UploadedDocument, analysis: DocumentAnalysis | null) => void
  setAiConfig: (config: Partial<Pick<WizardDraft, 'aiModel' | 'aiQuality' | 'creativity' | 'aiProvider'>>) => void
  setPublicationConfig: (config: Partial<WizardDraft>) => void
  applyPreset: (presetId: string) => void
  setEstimate: (estimate: JobEstimate) => void
  setActiveJob: (jobId: string) => void
  reset: () => void
}

export const useWizardStore = create<WizardState>()(
  persist(
    (set, get) => ({
      draft: DEFAULT_DRAFT,
      hasSavedDraft: false,

      goNext: () => set((s) => ({
        draft: { ...s.draft, step: Math.min(5, s.draft.step + 1) as WizardStep },
        hasSavedDraft: true,
      })),

      goBack: () => set((s) => ({
        draft: { ...s.draft, step: Math.max(1, s.draft.step - 1) as WizardStep },
      })),

      goToStep: (step) => set((s) => ({ draft: { ...s.draft, step } })),

      setDocument: (doc, analysis) => set((s) => ({
        draft: { ...s.draft, documentId: doc.id, filename: doc.filename, analysis },
        hasSavedDraft: true,
      })),

      setAiConfig: (config) => set((s) => ({
        draft: { ...s.draft, ...config },
        hasSavedDraft: true,
      })),

      setPublicationConfig: (config) => set((s) => ({
        draft: { ...s.draft, ...config },
        hasSavedDraft: true,
      })),

      applyPreset: (presetId) => {
        const preset = PRESETS.find((p) => p.id === presetId)
        if (!preset) return
        set((s) => ({
          draft: { ...s.draft, ...preset.config, presetId },
          hasSavedDraft: true,
        }))
      },

      setEstimate: (estimate) => set((s) => ({
        draft: { ...s.draft, estimate },
        hasSavedDraft: true,
      })),

      setActiveJob: (jobId) => set((s) => ({
        draft: { ...s.draft, activeJobId: jobId },
        hasSavedDraft: true,
      })),

      reset: () => {
        // Clear sessionStorage key directly to avoid stale state
        void get()
        set({ draft: { ...DEFAULT_DRAFT }, hasSavedDraft: false })
      },
    }),
    {
      name: 'wizard-draft',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
)
