import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Check } from 'lucide-react'
import type { WizardStep } from '@/types/ui'

const STEP_LABELS: Record<WizardStep, string> = {
  1: 'Upload',
  2: 'AI Config',
  3: 'Publication',
  4: 'Preview',
  5: 'Generate',
}

const STEPS: WizardStep[] = [1, 2, 3, 4, 5]

interface WizardNavProps {
  currentStep: WizardStep
  onBack?: () => void
  onNext?: () => void
  nextLabel?: string
  nextDisabled?: boolean
  nextLoading?: boolean
}

export function WizardNav({
  currentStep,
  onBack,
  onNext,
  nextLabel = 'Next',
  nextDisabled = false,
  nextLoading = false,
}: WizardNavProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2">
        {STEPS.map((step) => {
          const done = step < currentStep
          const active = step === currentStep
          return (
            <div key={step} className="flex items-center gap-2">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors',
                  done && 'border-primary bg-primary text-primary-foreground',
                  active && 'border-primary text-primary',
                  !done && !active && 'border-muted-foreground/30 text-muted-foreground'
                )}
                aria-label={`Step ${step}: ${STEP_LABELS[step]}${done ? ' (complete)' : active ? ' (current)' : ''}`}
              >
                {done ? <Check className="h-4 w-4" /> : step}
              </div>
              <span className={cn('text-xs hidden sm:block', active ? 'text-foreground font-medium' : 'text-muted-foreground')}>
                {STEP_LABELS[step]}
              </span>
              {step < 5 && <div className="h-px w-4 bg-border flex-shrink-0" />}
            </div>
          )
        })}
      </div>

      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={onBack}
          disabled={currentStep <= 1 || !onBack}
          className={currentStep <= 1 ? 'invisible' : undefined}
        >
          Back
        </Button>
        {onNext && (
          <Button onClick={onNext} disabled={nextDisabled || nextLoading}>
            {nextLoading ? 'Loading…' : nextLabel}
          </Button>
        )}
      </div>
    </div>
  )
}
