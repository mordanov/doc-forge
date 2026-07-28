import { useI18nStore } from '@/stores/i18nStore'
import type { Translations } from '@/i18n/en'

export function useT(): Translations {
  return useI18nStore((s) => s.t)
}
