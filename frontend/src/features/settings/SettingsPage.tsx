import { useState } from 'react'
import { useSettingsStore } from './settingsStore'
import { useTheme } from '@/hooks/useTheme'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Check } from 'lucide-react'
import { useT } from '@/hooks/useT'

const LANGUAGES = [
  { id: 'en', name: 'English' },
  { id: 'es', name: 'Spanish' },
  { id: 'fr', name: 'French' },
  { id: 'de', name: 'German' },
  { id: 'it', name: 'Italian' },
  { id: 'ru', name: 'Russian' },
]

const OUTPUT_FORMATS = [
  { id: 'docx', name: 'DOCX' },
  { id: 'pdf', name: 'PDF' },
  { id: 'html', name: 'HTML' },
  { id: 'markdown', name: 'Markdown' },
  { id: 'epub', name: 'EPUB' },
]

const TEMPLATES = [
  { id: 'minimal', name: 'Minimal' },
  { id: 'dk_eyewitness', name: 'DK Eyewitness' },
  { id: 'lonely_planet', name: 'Lonely Planet' },
  { id: 'corporate', name: 'Corporate' },
]

export default function SettingsPage() {
  const store = useSettingsStore()
  const settings = store.get()
  const { theme, toggleTheme } = useTheme()
  const t = useT()

  const [language, setLanguage] = useState(settings.defaultLanguage)
  const [outputFormat, setOutputFormat] = useState(settings.defaultOutputFormat)
  const [template, setTemplate] = useState(settings.defaultTemplate)
  const [apiKey, setApiKey] = useState(settings.openAiApiKey ?? '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  function handleSave() {
    setSaving(true)
    store.set({ defaultLanguage: language, defaultOutputFormat: outputFormat as typeof settings.defaultOutputFormat, defaultTemplate: template })
    store.setApiKey(apiKey || null)
    setTimeout(() => { setSaving(false); setSaved(true); setTimeout(() => setSaved(false), 2000) }, 300)
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold">{t.settings.title}</h1>

      <section className="space-y-4">
        <h2 className="text-base font-semibold">{t.settings.appearance}</h2>
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="dark-mode" className="text-sm">{t.settings.darkMode}</Label>
            <p className="text-xs text-muted-foreground">{t.settings.darkModeDesc}</p>
          </div>
          <Switch
            id="dark-mode"
            checked={theme === 'dark'}
            onCheckedChange={toggleTheme}
            aria-label="Toggle dark mode"
          />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-base font-semibold">{t.settings.defaults}</h2>

        <div className="space-y-2">
          <Label htmlFor="default-language">{t.settings.defaultLanguage}</Label>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger id="default-language">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {LANGUAGES.map((l) => <SelectItem key={l.id} value={l.id}>{l.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="default-format">{t.settings.defaultFormat}</Label>
          <Select value={outputFormat} onValueChange={(v) => setOutputFormat(v as typeof outputFormat)}>
            <SelectTrigger id="default-format">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {OUTPUT_FORMATS.map((f) => <SelectItem key={f.id} value={f.id}>{f.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="default-template">{t.settings.defaultTemplate}</Label>
          <Select value={template} onValueChange={setTemplate}>
            <SelectTrigger id="default-template">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {TEMPLATES.map((t2) => <SelectItem key={t2.id} value={t2.id}>{t2.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-base font-semibold">{t.settings.apiKeys}</h2>
        <div className="space-y-2">
          <Label htmlFor="openai-key">{t.settings.openAiKey}</Label>
          <Input
            id="openai-key"
            type="password"
            placeholder="sk-…"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            autoComplete="off"
          />
          <p className="text-xs text-muted-foreground">{t.settings.openAiKeyHint}</p>
        </div>
      </section>

      <Button onClick={handleSave} disabled={saving}>
        {saving ? (
          <><Loader2 className="h-4 w-4 animate-spin" />{t.settings.saving}</>
        ) : saved ? (
          <><Check className="h-4 w-4" />{t.settings.saved}</>
        ) : t.settings.save}
      </Button>
    </div>
  )
}
