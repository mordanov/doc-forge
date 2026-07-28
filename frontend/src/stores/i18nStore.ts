import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Lang = 'en' | 'ru'

interface I18nState {
  lang: Lang
  setLang: (lang: Lang) => void
}

function detectLang(): Lang {
  const browser = (typeof navigator !== 'undefined' ? navigator.language : '').split('-')[0].toLowerCase()
  return browser === 'ru' ? 'ru' : 'en'
}

export const useI18nStore = create<I18nState>()(
  persist(
    (set) => ({
      lang: detectLang(),
      setLang: (lang) => set({ lang }),
    }),
    { name: 'i18n' }
  )
)
