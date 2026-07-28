import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import en from '@/i18n/en'
import ru from '@/i18n/ru'
import type { Translations } from '@/i18n/en'

export type Lang = 'en' | 'ru'

const DICTS: Record<Lang, Translations> = { en, ru }

interface I18nState {
  lang: Lang
  t: Translations
  setLang: (lang: Lang) => void
}

function detectLang(): Lang {
  const saved = typeof localStorage !== 'undefined'
    ? (() => { try { return JSON.parse(localStorage.getItem('i18n') ?? '{}')?.state?.lang } catch { return undefined } })()
    : undefined
  if (saved === 'en' || saved === 'ru') return saved
  const browser = (typeof navigator !== 'undefined' ? navigator.language : '').split('-')[0].toLowerCase()
  return browser === 'ru' ? 'ru' : 'en'
}

export const useI18nStore = create<I18nState>()(
  persist(
    (set) => ({
      lang: detectLang(),
      t: DICTS[detectLang()],
      setLang: (lang) => set({ lang, t: DICTS[lang] }),
    }),
    { name: 'i18n' }
  )
)
