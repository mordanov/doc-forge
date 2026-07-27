import { useWizardStore } from '../wizardStore'
import { WizardNav } from '@/components/WizardNav'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'

const AI_MODELS = [
  { id: 'gpt-5.6', name: 'GPT-5.6' },
  { id: 'gpt-5.6-mini', name: 'GPT-5.6 Mini' },
  { id: 'gpt-5.6-sol', name: 'GPT-5.6 Solaris' },
  { id: 'gpt-5.5', name: 'GPT-5.5' },
]

const QUALITY_OPTIONS = [
  { id: 'fast', name: 'Fast', description: 'Quicker results, lower cost' },
  { id: 'balanced', name: 'Balanced', description: 'Good quality, reasonable speed' },
  { id: 'maximum', name: 'Maximum Quality', description: 'Best results, takes longer' },
] as const

const CREATIVITY_DESCRIPTIONS: Record<number, string> = {
  1: 'Strictly factual — no creative rewriting',
  2: 'Minimal creative input',
  3: 'Light editorial touch',
  4: 'Some rewriting for clarity',
  5: 'Balanced — moderate creative input',
  6: 'Enhanced readability and flow',
  7: 'Notable creative rewriting',
  8: 'Strong editorial voice',
  9: 'High creativity — significant rewrites',
  10: 'Maximum creativity — fully reimagined prose',
}

export function Step2AiConfig() {
  const { draft, setAiConfig, goNext, goBack } = useWizardStore()

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">AI Configuration</h2>
        <p className="text-sm text-muted-foreground">Choose how the AI processes your document</p>
      </div>

      <div className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="ai-provider">AI Provider</Label>
          <Select value="openai" disabled>
            <SelectTrigger id="ai-provider" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="openai">OpenAI</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">Only OpenAI is supported in this version</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="ai-model">Model</Label>
          <Select value={draft.aiModel} onValueChange={(v) => setAiConfig({ aiModel: v })}>
            <SelectTrigger id="ai-model" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {AI_MODELS.map((m) => (
                <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Quality</Label>
          <div className="flex gap-2">
            {QUALITY_OPTIONS.map((q) => (
              <button
                key={q.id}
                type="button"
                onClick={() => setAiConfig({ aiQuality: q.id })}
                aria-pressed={draft.aiQuality === q.id}
                title={q.description}
                className={`flex-1 rounded-md border px-3 py-2 text-sm transition-colors hover:bg-accent ${draft.aiQuality === q.id ? 'border-primary bg-accent font-medium' : ''}`}
              >
                {q.name}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="creativity">Creativity</Label>
            <span className="text-sm font-medium">{draft.creativity}</span>
          </div>
          <Slider
            id="creativity"
            min={1}
            max={10}
            step={1}
            value={[draft.creativity]}
            onValueChange={([v]) => setAiConfig({ creativity: v })}
            aria-label="Creativity level"
          />
          <p className="text-xs text-muted-foreground">
            {CREATIVITY_DESCRIPTIONS[draft.creativity]}
          </p>
        </div>
      </div>

      <WizardNav currentStep={2} onBack={goBack} onNext={goNext} />
    </div>
  )
}
