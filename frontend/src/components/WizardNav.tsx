import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Check } from 'lucide-react'
import type { WizardStep } from '@/types/ui'
import { useT } from '@/hooks/useT'

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
  nextLabel,
  nextDisabled = false,
  nextLoading = false,
}: WizardNavProps) {
  const t = useT()
  const label = nextLabel ?? t.wizardNav.next

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2">
        {STEPS.map((step) => {
          const done = step < currentStep
          const active = step === currentStep
          const stepLabel = t.wizardNav.steps[step]
          return (
            <div key={step} className="flex items-center gap-2">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors',
                  done && 'border-primary bg-primary text-primary-foreground',
                  active && 'border-primary text-primary',
                  !done && !active && 'border-muted-foreground/30 text-muted-foreground'
                )}
                aria-label={`Step ${step}: ${stepLabel}${done ? ' (complete)' : active ? ' (current)' : ''}`}
              >
                {done ? <Check className="h-4 w-4" /> : step}
              </div>
              <span className={cn('text-xs hidden sm:block', active ? 'text-foreground font-medium' : 'text-muted-foreground')}>
                {stepLabel}
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
          {t.wizardNav.back}
        </Button>
        {onNext && (
          <Button onClick={onNext} disabled={nextDisabled || nextLoading}>
            {nextLoading ? t.wizardNav.loading : label}
          </Button>
        )}
      </div>
    </div>
  )
}
