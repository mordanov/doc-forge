import { useWizardStore } from '../wizardStore'
import { useJob } from '../services/hooks/useJob'
import { ProgressTimeline, type ProgressStage } from '@/components/ProgressTimeline'
import { Button } from '@/components/ui/button'
import { downloadJob } from '../services/jobsService'
import { useNavigate } from 'react-router-dom'
import type { RenderStage } from '@/types/api'
import {
  Upload, Search, Brain, Image, Download, Cog, CheckCircle, ShieldCheck, Package, Flag,
  WifiOff,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useT } from '@/hooks/useT'

const STAGE_ICONS: Record<RenderStage, LucideIcon> = {
  UPLOADING: Upload,
  LOADING: Download,
  ANALYSING: Search,
  AI_PROCESSING: Brain,
  IMAGE_SEARCH: Image,
  IMAGE_DOWNLOAD: Download,
  RENDERING: Cog,
  VALIDATION: ShieldCheck,
  EXPORT: Package,
  FINISHED: Flag,
}

const STAGE_ORDER: RenderStage[] = [
  'UPLOADING', 'LOADING', 'ANALYSING', 'AI_PROCESSING',
  'IMAGE_SEARCH', 'IMAGE_DOWNLOAD', 'RENDERING', 'VALIDATION', 'EXPORT', 'FINISHED',
]

function getStageStatus(
  stageId: RenderStage,
  currentStage: RenderStage,
  jobStatus: string
): ProgressStage['status'] {
  const current = STAGE_ORDER.indexOf(currentStage)
  const mine = STAGE_ORDER.indexOf(stageId)
  if (jobStatus === 'FAILED' && stageId === currentStage) return 'error'
  if (mine < current) return 'complete'
  if (mine === current) return jobStatus === 'COMPLETED' ? 'complete' : 'active'
  return 'pending'
}

export function Step5Rendering() {
  const { draft, reset } = useWizardStore()
  const { data: job, connectionLost } = useJob(draft.activeJobId, { pollingInterval: 3000 })
  const navigate = useNavigate()
  const t = useT()

  const stages: ProgressStage[] = STAGE_ORDER.map((id) => ({
    id,
    label: t.step5.stages[id],
    icon: STAGE_ICONS[id],
    status: job ? getStageStatus(id, job.stage, job.status) : 'pending',
    progress: job?.stage === id && job.status === 'RUNNING' ? job.progress : undefined,
    elapsedSeconds: job?.stage === id ? job.elapsed_seconds : undefined,
  }))

  async function handleDownload() {
    if (!draft.activeJobId) return
    const fmt = draft.outputFormats[0] ?? 'docx'
    await downloadJob(draft.activeJobId, fmt)
  }

  function handleDone() {
    reset()
    navigate('/projects')
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t.step5.title}</h2>
        <p className="text-sm text-muted-foreground">{draft.filename}</p>
      </div>

      {connectionLost && (
        <div className="flex items-center gap-2 rounded-lg border border-orange-400/50 bg-orange-50 dark:bg-orange-900/20 px-4 py-3 text-sm text-orange-700 dark:text-orange-300">
          <WifiOff className="h-4 w-4 shrink-0" />
          {t.step5.connectionLost}
        </div>
      )}

      <ProgressTimeline stages={stages} currentStage={job?.stage ?? 'UPLOADING'} />

      {job?.status === 'COMPLETED' && (
        <div className="flex gap-3 mt-2">
          <Button onClick={handleDownload}>
            <Download className="h-4 w-4" />
            {t.step5.download}
          </Button>
          <Button variant="outline" onClick={handleDone}>
            {t.step5.viewProjects}
          </Button>
        </div>
      )}

      {job?.status === 'FAILED' && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 space-y-2">
          <div className="flex items-center gap-2 text-destructive">
            <CheckCircle className="h-4 w-4" />
            <p className="text-sm font-medium">{t.step5.failed}</p>
          </div>
          {job.error && <p className="text-xs text-destructive">{job.error}</p>}
          <button
            type="button"
            onClick={() => navigate('/settings')}
            className="text-xs text-primary underline"
          >
            {t.step5.backToSettings}
          </button>
        </div>
      )}

      {job?.status === 'CANCELLED' && (
        <div className="rounded-lg border p-4 text-sm text-muted-foreground">
          {t.step5.cancelled}
        </div>
      )}
    </div>
  )
}
