import { useQuery } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
import { THEME_METADATA } from '@/features/wizard/themeMetadata'
import api from '@/lib/api'
import type { Theme } from '@/types/api'

interface ThemeGalleryProps {
  selected: string
  onChange: (themeId: string) => void
  disabled?: boolean
}

function useThemes() {
  return useQuery({
    queryKey: ['themes'],
    queryFn: async () => {
      const { data } = await api.get<Theme[]>('/system/themes')
      return data
    },
    staleTime: Infinity,
  })
}

export function ThemeGallery({ selected, onChange, disabled = false }: ThemeGalleryProps) {
  const { data: themes = [], isLoading } = useThemes()

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {themes.map((theme) => {
        const meta = THEME_METADATA[theme.id]
        const name = meta?.name ?? theme.id
        const description = meta?.description ?? ''
        const primaryColor = meta?.primaryColor ?? '#888'
        const imgSrc = `/theme-previews/${theme.id}.png`

        return (
          <button
            key={theme.id}
            type="button"
            disabled={disabled}
            onClick={() => onChange(theme.id)}
            className={cn(
              'flex flex-col rounded-lg border overflow-hidden text-left transition-colors hover:border-primary',
              selected === theme.id && 'border-primary ring-1 ring-primary',
              disabled && 'pointer-events-none opacity-50'
            )}
            aria-pressed={selected === theme.id}
            aria-label={`${name}: ${description}`}
          >
            <div className="h-20 relative">
              <img
                src={imgSrc}
                alt={name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const el = e.currentTarget
                  el.style.display = 'none'
                  const swatch = el.nextSibling as HTMLElement | null
                  if (swatch) swatch.style.display = 'flex'
                }}
              />
              <div
                className="absolute inset-0 items-center justify-center text-white text-sm font-bold"
                style={{ background: primaryColor, display: 'none' }}
              >
                {name}
              </div>
            </div>
            <div className="p-2">
              <p className="text-xs font-medium">{name}</p>
              <p className="text-xs text-muted-foreground line-clamp-1">{description}</p>
            </div>
          </button>
        )
      })}
    </div>
  )
}
