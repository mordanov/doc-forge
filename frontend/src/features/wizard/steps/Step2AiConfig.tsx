import { useWizardStore } from '../wizardStore'
import { WizardNav } from '@/components/WizardNav'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { useT } from '@/hooks/useT'

const AI_MODELS = [
  { id: 'gpt-5.6-sol', name: 'GPT-5.6 Sol' },
  { id: 'gpt-5.6-luna', name: 'GPT-5.6 Luna' },
  { id: 'gpt-5.6-terra', name: 'GPT-5.6 Terra' },
  { id: 'gpt-5.5-pro', name: 'GPT-5.5 Pro' },
  { id: 'gpt-5.5', name: 'GPT-5.5' },
  { id: 'gpt-5.4-pro', name: 'GPT-5.4 Pro' },
  { id: 'gpt-5.4', name: 'GPT-5.4' },
  { id: 'gpt-5.4-mini', name: 'GPT-5.4 Mini' },
  { id: 'gpt-5.4-nano', name: 'GPT-5.4 Nano' },
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
  { id: 'gpt-4.1', name: 'GPT-4.1' },
  { id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini' },
  { id: 'o3', name: 'o3' },
  { id: 'o4-mini', name: 'o4-mini' },
]

const QUALITY_IDS = ['fast', 'balanced', 'maximum'] as const

export function Step2AiConfig() {
  const { draft, setAiConfig, goNext, goBack } = useWizardStore()
  const t = useT()

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t.step2.title}</h2>
        <p className="text-sm text-muted-foreground">{t.step2.subtitle}</p>
      </div>

      <div className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="ai-provider">{t.step2.provider}</Label>
          <Select value="openai" disabled>
            <SelectTrigger id="ai-provider" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="openai">OpenAI</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">{t.step2.providerOnly}</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="ai-model">{t.step2.model}</Label>
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
          <Label>{t.step2.quality}</Label>
          <div className="flex gap-2">
            {QUALITY_IDS.map((id) => (
              <button
                key={id}
                type="button"
                onClick={() => setAiConfig({ aiQuality: id })}
                aria-pressed={draft.aiQuality === id}
                title={t.step2.qualityDescs[id]}
                className={`flex-1 rounded-md border px-3 py-2 text-sm transition-colors hover:bg-accent ${draft.aiQuality === id ? 'border-primary bg-accent font-medium' : ''}`}
              >
                {t.step2.qualityOptions[id]}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="creativity">{t.step2.creativity}</Label>
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
            {t.step2.creativityDescriptions[draft.creativity as keyof typeof t.step2.creativityDescriptions]}
          </p>
        </div>
      </div>

      <WizardNav currentStep={2} onBack={goBack} onNext={goNext} />
    </div>
  )
}
