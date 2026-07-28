import { useI18nStore, type Lang } from '@/stores/i18nStore'

const OPTIONS: { value: Lang; label: string }[] = [
  { value: 'en', label: 'EN' },
  { value: 'ru', label: 'RU' },
]

export function LangSwitch() {
  const { lang, setLang } = useI18nStore()

  return (
    <div className="flex items-center gap-1 text-xs font-medium">
      {OPTIONS.map(({ value, label }, i) => (
        <span key={value} className="flex items-center gap-1">
          {i > 0 && <span className="text-muted-foreground/40">|</span>}
          <button
            type="button"
            onClick={() => setLang(value)}
            className={
              lang === value
                ? 'text-foreground'
                : 'text-muted-foreground hover:text-foreground transition-colors'
            }
            aria-pressed={lang === value}
            aria-label={`Switch language to ${value.toUpperCase()}`}
          >
            {label}
          </button>
        </span>
      ))}
    </div>
  )
}
