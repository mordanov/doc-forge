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

const STAGE_CONFIG: { id: RenderStage; label: string; icon: LucideIcon }[] = [
  { id: 'UPLOADING', label: 'Uploading', icon: Upload },
  { id: 'LOADING', label: 'Loading', icon: Download },
  { id: 'ANALYSING', label: 'Analysing', icon: Search },
  { id: 'AI_PROCESSING', label: 'AI Processing', icon: Brain },
  { id: 'IMAGE_SEARCH', label: 'Searching Images', icon: Image },
  { id: 'IMAGE_DOWNLOAD', label: 'Downloading Images', icon: Download },
  { id: 'RENDERING', label: 'Rendering', icon: Cog },
  { id: 'VALIDATION', label: 'Validation', icon: ShieldCheck },
  { id: 'EXPORT', label: 'Export', icon: Package },
  { id: 'FINISHED', label: 'Finished', icon: Flag },
]

const STAGE_ORDER = STAGE_CONFIG.map((s) => s.id)

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

  const stages: ProgressStage[] = STAGE_CONFIG.map(({ id, label, icon }) => ({
    id,
    label,
    icon,
    status: job ? getStageStatus(id, job.stage, job.status) : 'pending',
    progress: job?.stage === id && job.status === 'RUNNING' ? job.progress : undefined,
    elapsedSeconds: job?.stage === id ? job.elapsed_seconds : undefined,
  }))

  function handleDownload() {
    if (!draft.activeJobId) return
    const fmt = draft.outputFormats[0] ?? 'docx'
    downloadJob(draft.activeJobId, fmt)
  }

  function handleDone() {
    reset()
    navigate('/projects')
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Generating</h2>
        <p className="text-sm text-muted-foreground">{draft.filename}</p>
      </div>

      {connectionLost && (
        <div className="flex items-center gap-2 rounded-lg border border-orange-400/50 bg-orange-50 dark:bg-orange-900/20 px-4 py-3 text-sm text-orange-700 dark:text-orange-300">
          <WifiOff className="h-4 w-4 shrink-0" />
          Connection lost — retrying…
        </div>
      )}

      <ProgressTimeline stages={stages} currentStage={job?.stage ?? 'UPLOADING'} />

      {job?.status === 'COMPLETED' && (
        <div className="flex gap-3 mt-2">
          <Button onClick={handleDownload}>
            <Download className="h-4 w-4" />
            Download
          </Button>
          <Button variant="outline" onClick={handleDone}>
            View Projects
          </Button>
        </div>
      )}

      {job?.status === 'FAILED' && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 space-y-2">
          <div className="flex items-center gap-2 text-destructive">
            <CheckCircle className="h-4 w-4" />
            <p className="text-sm font-medium">Generation failed</p>
          </div>
          {job.error && <p className="text-xs text-destructive">{job.error}</p>}
          <button
            type="button"
            onClick={() => navigate('/settings')}
            className="text-xs text-primary underline"
          >
            Back to settings
          </button>
        </div>
      )}

      {job?.status === 'CANCELLED' && (
        <div className="rounded-lg border p-4 text-sm text-muted-foreground">
          Job was cancelled.
        </div>
      )}
    </div>
  )
}
