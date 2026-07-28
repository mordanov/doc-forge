import { useState } from 'react'
import { useWizardStore } from '../wizardStore'
import { PRESETS } from '../presets'
import { WizardNav } from '@/components/WizardNav'
import { PresetSelector } from '@/components/PresetSelector'
import { ThemeGallery } from '@/components/ThemeGallery'
import { ColourPicker } from '@/components/ColourPicker'
import { HintIcon } from '@/components/HintIcon'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useT } from '@/hooks/useT'

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
  const t = useT()

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
        <h2 className="text-xl font-semibold mb-1">{t.step3.title}</h2>
        <p className="text-sm text-muted-foreground">{t.step3.subtitle}</p>
      </div>

      <section className="space-y-3">
        <div className="flex items-center gap-1">
          <Label className="text-sm font-semibold">{t.step3.preset}</Label>
          <HintIcon text={t.step3.hints.preset} />
        </div>
        <PresetSelector
          presets={PRESETS}
          selected={draft.presetId}
          onChange={applyPreset}
        />
      </section>

      <section className="space-y-3">
        <div className="flex items-center gap-1">
          <Label className="text-sm font-semibold">{t.step3.theme}</Label>
          <HintIcon text={t.step3.hints.theme} />
        </div>
        <ThemeGallery selected={draft.template} onChange={(id) => setPublicationConfig({ template: id })} />
      </section>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="language">{t.step3.language}</Label>
            <HintIcon text={t.step3.hints.language} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label>{t.step3.outputFormats}</Label>
            <HintIcon text={t.step3.hints.outputFormats} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label htmlFor="image-density">{t.step3.imageDensity}</Label>
            <HintIcon text={t.step3.hints.imageDensity} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label htmlFor="layout-density">{t.step3.layoutDensity}</Label>
            <HintIcon text={t.step3.hints.layoutDensity} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label htmlFor="colour-palette">{t.step3.colourPalette}</Label>
            <HintIcon text={t.step3.hints.colourPalette} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label htmlFor="validation-level">{t.step3.validationLevel}</Label>
            <HintIcon text={t.step3.hints.validationLevel} />
          </div>
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
          <div className="flex items-center gap-1">
            <Label htmlFor="offline-mode" className="text-sm">{t.step3.offlineMode}</Label>
            <HintIcon text={t.step3.hints.offlineMode} />
          </div>
          <p className="text-xs text-muted-foreground">{t.step3.offlineModeDesc}</p>
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
        {t.step3.advancedSettings}
      </button>

      {advancedOpen && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-lg border p-4 bg-muted/30">
          {[
            { id: 'parallel-downloads', label: t.step3.parallelDownloads, hint: t.step3.hints.parallelDownloads, value: draft.parallelDownloads, key: 'parallelDownloads' as const },
            { id: 'retry-count', label: t.step3.retryCount, hint: t.step3.hints.retryCount, value: draft.retryCount, key: 'retryCount' as const },
            { id: 'timeout', label: t.step3.timeout, hint: t.step3.hints.timeout, value: draft.timeout, key: 'timeout' as const },
          ].map(({ id, label, hint, value, key }) => (
            <div key={id} className="space-y-1">
              <div className="flex items-center gap-1">
                <Label htmlFor={id} className="text-xs">{label}</Label>
                <HintIcon text={hint} />
              </div>
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
