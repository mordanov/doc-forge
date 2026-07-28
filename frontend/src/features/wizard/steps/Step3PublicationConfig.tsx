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
const IMAGE_SOURCES = ['wikimedia', 'pexels', 'unsplash'] as const

export function Step3PublicationConfig() {
  const { draft, setPublicationConfig, applyPreset, goNext, goBack } = useWizardStore()
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const t = useT()

  function selectFormat(fmt: typeof OUTPUT_FORMATS[number]) {
    setPublicationConfig({ outputFormat: fmt })
  }

  function selectSource(src: string) {
    setPublicationConfig({ imageSource: src })
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
        {/* Language */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="language">{t.step3.language}</Label>
            <HintIcon text={t.step3.hints.language} />
          </div>
          <Select value={draft.language} onValueChange={(v) => setPublicationConfig({ language: v })}>
            <SelectTrigger id="language"><SelectValue /></SelectTrigger>
            <SelectContent>
              {LANGUAGES.map((l) => <SelectItem key={l.id} value={l.id}>{l.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        {/* Output Formats */}
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
                aria-pressed={draft.outputFormat === fmt}
                onClick={() => selectFormat(fmt)}
                className={`rounded border px-3 py-1 text-xs transition-colors ${draft.outputFormat === fmt ? 'border-primary bg-accent font-medium' : 'hover:bg-accent'}`}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Typography */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="typography">{t.step3.typography}</Label>
            <HintIcon text={t.step3.hints.typography} />
          </div>
          <Select value={draft.typography} onValueChange={(v) => setPublicationConfig({ typography: v })}>
            <SelectTrigger id="typography"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['conservative', 'editorial', 'magazine', 'luxury'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Sidebar Style */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="sidebar-style">{t.step3.sidebarStyle}</Label>
            <HintIcon text={t.step3.hints.sidebarStyle} />
          </div>
          <Select value={draft.sidebarStyle} onValueChange={(v) => setPublicationConfig({ sidebarStyle: v })}>
            <SelectTrigger id="sidebar-style"><SelectValue /></SelectTrigger>
            <SelectContent>
              {['none', 'minimal', 'editorial', 'magazine'].map((v) => (
                <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Cover Page */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="cover-page">{t.step3.coverPage}</Label>
            <HintIcon text={t.step3.hints.coverPage} />
          </div>
          <Select value={draft.coverPage} onValueChange={(v) => setPublicationConfig({ coverPage: v })}>
            <SelectTrigger id="cover-page"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[
                { value: 'auto', label: 'Auto' },
                { value: 'photo', label: 'Photo' },
                { value: 'minimal', label: 'Minimal' },
                { value: 'illustration', label: 'Illustration' },
                { value: 'none', label: 'None' },
              ].map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Table of Contents */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="toc">{t.step3.tableOfContents}</Label>
            <HintIcon text={t.step3.hints.tableOfContents} />
          </div>
          <Select value={draft.tableOfContents} onValueChange={(v) => setPublicationConfig({ tableOfContents: v })}>
            <SelectTrigger id="toc"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[
                { value: 'generate', label: 'Generate' },
                { value: 'update_existing', label: 'Update Existing' },
                { value: 'keep_existing', label: 'Keep Existing' },
              ].map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Headers & Footers */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="headers-footers">{t.step3.headersFooters}</Label>
            <HintIcon text={t.step3.hints.headersFooters} />
          </div>
          <Select value={draft.headersFooters} onValueChange={(v) => setPublicationConfig({ headersFooters: v })}>
            <SelectTrigger id="headers-footers"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[
                { value: 'generate', label: 'Generate' },
                { value: 'replace_existing', label: 'Replace Existing' },
                { value: 'keep_existing', label: 'Keep Existing' },
              ].map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Image Density */}
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

        {/* Layout Density */}
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

        {/* Colour Palette */}
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

        {/* Validation Level */}
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

        {/* Image Policy */}
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <Label htmlFor="image-policy">{t.step3.imagePolicy}</Label>
            <HintIcon text={t.step3.hints.imagePolicy} />
          </div>
          <Select value={draft.imagePolicy} onValueChange={(v) => setPublicationConfig({ imagePolicy: v as typeof draft.imagePolicy })}>
            <SelectTrigger id="image-policy"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[
                { value: 'auto', label: 'Auto' },
                { value: 'placeholders_only', label: 'Placeholders Only' },
                { value: 'preserve', label: 'Preserve Original' },
                { value: 'disable', label: 'Disable Images' },
              ].map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Image Sources */}
      <div className="space-y-2">
        <div className="flex items-center gap-1">
          <Label>{t.step3.imageSources}</Label>
          <HintIcon text={t.step3.hints.imageSources} />
        </div>
        <div className="flex flex-wrap gap-2">
          {IMAGE_SOURCES.map((src) => (
            <button
              key={src}
              type="button"
              aria-pressed={draft.imageSource === src}
              onClick={() => selectSource(src)}
              className={`rounded border px-3 py-1 text-xs transition-colors capitalize ${draft.imageSource === src ? 'border-primary bg-accent font-medium' : 'hover:bg-accent'}`}
            >
              {src}
            </button>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">{t.step3.imageSourcesDesc}</p>
      </div>

      {/* Offline Mode */}
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

      {/* Advanced Settings */}
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
