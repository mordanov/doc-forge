import type { LucideIcon } from 'lucide-react'
import { cn, formatDuration } from '@/lib/utils'
import { Check, Loader2, AlertCircle, Clock } from 'lucide-react'

export interface ProgressStage {
  id: string
  label: string
  icon: LucideIcon
  status: 'pending' | 'active' | 'complete' | 'error'
  progress?: number
  elapsedSeconds?: number
  detail?: string
}

interface ProgressTimelineProps {
  stages: ProgressStage[]
  currentStage: string
}

export function ProgressTimeline({ stages, currentStage: _currentStage }: ProgressTimelineProps) {
  return (
    <div className="flex flex-col gap-3">
      {stages.map((stage) => {
        const Icon = stage.icon
        return (
          <div key={stage.id} className="flex items-start gap-3">
            <div
              className={cn(
                'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2',
                stage.status === 'complete' && 'border-primary bg-primary text-primary-foreground',
                stage.status === 'active' && 'border-primary text-primary',
                stage.status === 'error' && 'border-destructive text-destructive',
                stage.status === 'pending' && 'border-muted-foreground/30 text-muted-foreground'
              )}
              aria-label={`${stage.label}: ${stage.status}`}
            >
              {stage.status === 'complete' && <Check className="h-4 w-4" />}
              {stage.status === 'active' && <Loader2 className="h-4 w-4 animate-spin" />}
              {stage.status === 'error' && <AlertCircle className="h-4 w-4" />}
              {stage.status === 'pending' && <Icon className="h-4 w-4" />}
            </div>

            <div className="flex-1 min-w-0 pt-0.5">
              <div className="flex items-center justify-between gap-2">
                <p className={cn(
                  'text-sm font-medium',
                  stage.status === 'pending' && 'text-muted-foreground'
                )}>
                  {stage.label}
                </p>
                {stage.elapsedSeconds != null && stage.status !== 'pending' && (
                  <span className="text-xs text-muted-foreground flex items-center gap-1 shrink-0">
                    <Clock className="h-3 w-3" />
                    {formatDuration(stage.elapsedSeconds)}
                  </span>
                )}
              </div>

              {stage.status === 'active' && stage.detail && (
                <p className="text-xs text-muted-foreground mt-0.5 truncate">{stage.detail}</p>
              )}

              {stage.status === 'active' && stage.progress != null && (
                <div className="mt-1 h-1.5 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-primary transition-all duration-500"
                    style={{ width: `${stage.progress}%` }}
                    role="progressbar"
                    aria-valuenow={stage.progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  />
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
