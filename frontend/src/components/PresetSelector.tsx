import { cn } from '@/lib/utils'
import type { Preset } from '@/types/ui'

interface PresetSelectorProps {
  presets: Preset[]
  selected: string | null
  onChange: (presetId: string) => void
}

export function PresetSelector({ presets, selected, onChange }: PresetSelectorProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {presets.map((preset) => (
        <button
          key={preset.id}
          type="button"
          onClick={() => onChange(preset.id)}
          className={cn(
            'flex flex-col gap-1 rounded-lg border p-3 text-left transition-colors hover:bg-accent',
            selected === preset.id && 'border-primary bg-accent ring-1 ring-primary'
          )}
          aria-pressed={selected === preset.id}
          aria-label={`${preset.name}: ${preset.description}`}
        >
          <span className="text-sm font-medium">{preset.name}</span>
          <span className="text-xs text-muted-foreground line-clamp-2">{preset.description}</span>
        </button>
      ))}
    </div>
  )
}
