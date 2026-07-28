import { useI18nStore } from '@/stores/i18nStore'
import en from '@/i18n/en'
import ru from '@/i18n/ru'
import type { Translations } from '@/i18n/en'

const DICTS: Record<string, Translations> = { en, ru }

export function useT(): Translations {
  const lang = useI18nStore((s) => s.lang)
  return DICTS[lang] ?? en
}
