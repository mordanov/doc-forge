import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { useThemeStore } from '@/stores/themeStore'
import type { AppSettings, OutputFormat } from '@/types/ui'

const SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'ru']

function detectBrowserLanguage(): string {
  const lang = (typeof navigator !== 'undefined' ? navigator.language : '') || ''
  const code = lang.split('-')[0].toLowerCase()
  return SUPPORTED_LANGUAGES.includes(code) ? code : 'en'
}

const DEFAULT_SETTINGS: AppSettings = {
  theme: 'light',
  defaultLanguage: detectBrowserLanguage(),
  defaultOutputFormat: 'docx',
  defaultTemplate: 'minimal',
  openAiApiKey: null,
}

interface SettingsState {
  settings: AppSettings
  get: () => AppSettings
  set: (partial: Partial<AppSettings>) => void
  setApiKey: (key: string | null) => void
  getApiKey: () => string | null
  reset: () => void
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      settings: DEFAULT_SETTINGS,

      get: () => get().settings,

      set: (partial) => {
        const next = { ...get().settings, ...partial }
        if (partial.theme) {
          useThemeStore.getState().setTheme(partial.theme as 'light' | 'dark')
        }
        set({ settings: next })
      },

      setApiKey: (key) => {
        set((s) => ({ settings: { ...s.settings, openAiApiKey: key } }))
      },

      getApiKey: () => get().settings.openAiApiKey,

      reset: () => {
        useThemeStore.getState().setTheme(DEFAULT_SETTINGS.theme)
        set({ settings: DEFAULT_SETTINGS })
      },
    }),
    { name: 'settings' }
  )
)

export function useDefaultsForWizard(): { language: string; outputFormat: OutputFormat; template: string } {
  const settings = useSettingsStore((s) => s.settings)
  return {
    language: settings.defaultLanguage,
    outputFormat: settings.defaultOutputFormat,
    template: settings.defaultTemplate,
  }
}
