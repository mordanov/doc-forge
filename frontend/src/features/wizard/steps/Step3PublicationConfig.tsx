import { useState } from 'react'
import { useWizardStore } from '../wizardStore'
import { PRESETS } from '../presets'
import { WizardNav } from '@/components/WizardNav'
import { PresetSelector } from '@/components/PresetSelector'
import { ThemeGallery } from '@/components/ThemeGallery'
import { ColourPicker } from '@/components/ColourPicker'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { ChevronDown, ChevronUp } from 'lucide-react'

const LANGUAGES = [
  { id: 'en', name: 'English' },
  { id: 'es', name: 'Spanish' },
  { id: 'fr', name: 'French' },
  { id: 'de', name: 'German' },
  { id: 'it', name: 'Italian' },
  { id: 'ru', name: 'Russian' },
]

const OUTPUT_FORMATS = ['docx', 'pdf', 'html', 'markdown', 'epub'] as const

export function Step3PublicationConfig() {
  const { draft, setPublicationConfig, applyPreset, goNext, goBack } = useWizardStore()
  const [advancedOpen, setAdvancedOpen] = useState(false)

  function toggleFormat(fmt: string) {
    const current = draft.outputFormats
    const updated = current.includes(fmt as typeof OUTPUT_FORMATS[number])
      ? current.filter((f) => f !== fmt)
      : [...current, fmt as typeof OUTPUT_FORMATS[number]]
    if (updated.length > 0) setPublicationConfig({ outputFormats: updated })
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Publication Configuration</h2>
        <p className="text-sm text-muted-foreground">Choose a preset or configure settings individually</p>
      </div>

      <section className="space-y-3">
        <Label className="text-sm font-semibold">Preset</Label>
        <PresetSelector
          presets={PRESETS}
          selected={draft.presetId}
          onChange={applyPreset}
        />
      </section>

      <section className="space-y-3">
        <Label className="text-sm font-semibold">Theme</Label>
        <ThemeGallery selected={draft.template} onChange={(id) => setPublicationConfig({ template: id })} />
      </section>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="language">Language</Label>
          <Select value={draft.language} onValueChange={(v) => setPublicationConfig({ language: v })}>
            <SelectTrigger id="language">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {LANGUAGES.map((l) => <SelectItem key={l.id} value={l.id}>{l.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Output Formats</Label>
          <div className="flex flex-wrap gap-2">
            {OUTPUT_FORMATS.map((fmt) => (
              <button
                key={fmt}
                type="button"
                aria-pressed={draft.outputFormats.includes(fmt)}
                onClick={() => toggleFormat(fmt)}
                className={`rounded border px-3 py-1 text-xs transition-colors ${draft.outputFormats.includes(fmt) ? 'border-primary bg-accent font-medium' : 'hover:bg-accent'}`}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="image-density">Image Density</Label>
          <Select value={draft.imageDensity} onValueChange={(v) => setPublicationConfig({ imageDensity: v as typeof draft.imageDensity })}>
            <SelectTrigger id="image-density"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['minimal', 'balanced', 'illustrated', 'maximum'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="layout-density">Layout Density</Label>
          <Select value={draft.layoutDensity} onValueChange={(v) => setPublicationConfig({ layoutDensity: v as typeof draft.layoutDensity })}>
            <SelectTrigger id="layout-density"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['compact', 'balanced', 'spacious'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="colour-palette">Colour Palette</Label>
          <Select value={draft.colourPalette} onValueChange={(v) => setPublicationConfig({ colourPalette: v })}>
            <SelectTrigger id="colour-palette"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['auto', 'warm', 'cool', 'monochrome', 'custom'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {draft.colourPalette === 'custom' && (
            <ColourPicker
              value={draft.customColour}
              onChange={(c) => setPublicationConfig({ customColour: c })}
            />
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="validation-level">Validation Level</Label>
          <Select value={draft.validationLevel} onValueChange={(v) => setPublicationConfig({ validationLevel: v as typeof draft.validationLevel })}>
            <SelectTrigger id="validation-level"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['fast', 'standard', 'strict'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <Label htmlFor="offline-mode" className="text-sm">Offline Mode</Label>
          <p className="text-xs text-muted-foreground">Use only cached resources</p>
        </div>
        <Switch
          id="offline-mode"
          checked={draft.offlineMode}
          onCheckedChange={(v) => setPublicationConfig({ offlineMode: v })}
        />
      </div>

      <button
        type="button"
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        onClick={() => setAdvancedOpen((o) => !o)}
        aria-expanded={advancedOpen}
      >
        {advancedOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        Advanced Settings
      </button>

      {advancedOpen && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-lg border p-4 bg-muted/30">
          {[
            { id: 'parallel-downloads', label: 'Parallel Downloads', value: draft.parallelDownloads, key: 'parallelDownloads' as const },
            { id: 'retry-count', label: 'Retry Count', value: draft.retryCount, key: 'retryCount' as const },
            { id: 'timeout', label: 'Timeout (s)', value: draft.timeout, key: 'timeout' as const },
          ].map(({ id, label, value, key }) => (
            <div key={id} className="space-y-1">
              <Label htmlFor={id} className="text-xs">{label}</Label>
              <input
                id={id}
                type="number"
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                value={value}
                onChange={(e) => setPublicationConfig({ [key]: parseInt(e.target.value) || 0 })}
              />
            </div>
          ))}
        </div>
      )}

      <WizardNav currentStep={3} onBack={goBack} onNext={goNext} />
    </div>
  )
}
