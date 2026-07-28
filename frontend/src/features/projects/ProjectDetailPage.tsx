import { useParams, useNavigate } from 'react-router-dom'
import { useProject } from './services/hooks/useProject'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { downloadJob } from '@/features/wizard/services/jobsService'
import { ArrowLeft, Download, Copy, Loader2, AlertCircle } from 'lucide-react'
import { useDuplicateProject } from './services/hooks/useDuplicateProject'
import { useT } from '@/hooks/useT'
import { cn } from '@/lib/utils'

const STATUS_COLOURS: Record<string, string> = {
  COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  RUNNING: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  QUEUED: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  CANCELLED: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const t = useT()
  const { data: project, isLoading, isError } = useProject(id ?? '')
  const duplicate = useDuplicateProject()

  if (isLoading) {
    return (
      <div className="p-8 max-w-3xl mx-auto flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isError || !project) {
    return (
      <div className="p-8 max-w-3xl mx-auto flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
        <AlertCircle className="h-10 w-10 opacity-40" />
        <p className="text-sm">Project not found.</p>
        <Button variant="outline" onClick={() => navigate('/projects')}>
          <ArrowLeft className="h-4 w-4" />
          {t.projects.title}
        </Button>
      </div>
    )
  }

  const canDownload = project.status === 'COMPLETED' && project.output_paths.length > 0
  const config = project.config_snapshot

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate('/projects')}>
          <ArrowLeft className="h-4 w-4" />
          {t.projects.title}
        </Button>
      </div>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{project.name || project.input_filename}</h1>
          <p className="text-sm text-muted-foreground mt-1">{project.input_filename}</p>
        </div>
        <span className={cn('shrink-0 rounded-full px-2.5 py-1 text-xs font-medium', STATUS_COLOURS[project.status] ?? STATUS_COLOURS.CANCELLED)}>
          {project.status}
        </span>
      </div>

      <div className="flex gap-3 flex-wrap">
        {canDownload && project.output_paths.map((p) => {
          const fmt = p.split('.').pop() ?? 'docx'
          return (
            <Button
              key={p}
              size="sm"
              onClick={() => void downloadJob(project.job_id, fmt)}
            >
              <Download className="h-4 w-4" />
              {t.projects.download} {fmt.toUpperCase()}
            </Button>
          )
        })}
        <Button
          size="sm"
          variant="outline"
          disabled={duplicate.isPending}
          onClick={() => duplicate.mutate(project.id, { onSuccess: () => navigate('/projects') })}
        >
          {duplicate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Copy className="h-4 w-4" />}
          {t.projects.duplicate}
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Publication Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <Row label="Template" value={project.template} />
            <Row label="Language" value={project.language} />
            <Row label="AI Model" value={project.ai_model} />
            <Row label="Created" value={new Date(project.created_at).toLocaleString()} />
            {project.completed_at && (
              <Row label="Completed" value={new Date(project.completed_at).toLocaleString()} />
            )}
          </CardContent>
        </Card>

        {config && Object.keys(config).length > 0 && (() => {
          const cfg = config as Record<string, string>
          const rows: { label: string; key: string }[] = [
            { label: 'Typography', key: 'typography' },
            { label: 'Cover Page', key: 'cover_page' },
            { label: 'Table of Contents', key: 'table_of_contents' },
            { label: 'Headers & Footers', key: 'headers_footers' },
            { label: 'Image Density', key: 'image_density' },
            { label: 'Layout Density', key: 'layout_density' },
            { label: 'Colour Palette', key: 'colour_palette' },
            { label: 'Sidebar Style', key: 'sidebar_style' },
            { label: 'Image Policy', key: 'image_policy' },
            { label: 'Validation Level', key: 'validation_level' },
          ]
          const visible = rows.filter((r) => cfg[r.key])
          if (visible.length === 0) return null
          return (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {visible.map((r) => (
                  <Row key={r.key} label={r.label} value={cfg[r.key]} />
                ))}
              </CardContent>
            </Card>
          )
        })()}
      </div>

      {project.output_paths.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Output Files</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {project.output_paths.map((p) => (
                <li key={p} className="text-xs text-muted-foreground font-mono truncate">{p}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium truncate">{value}</span>
    </div>
  )
}
