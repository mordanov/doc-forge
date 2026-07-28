import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ParsedProject } from '@/types/api'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { useDuplicateProject } from './services/hooks/useDuplicateProject'
import { useDeleteProject } from './services/hooks/useDeleteProject'
import { downloadJob } from '@/features/wizard/services/jobsService'
import { cn } from '@/lib/utils'
import { Loader2, Copy, Download, Trash2, ExternalLink } from 'lucide-react'
import { useT } from '@/hooks/useT'

const STATUS_COLOURS: Record<string, string> = {
  COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  RUNNING: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  QUEUED: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  CANCELLED: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
}

interface ProjectCardProps {
  project: ParsedProject
  loading?: boolean
}

export function ProjectCard({ project, loading }: ProjectCardProps) {
  const duplicate = useDuplicateProject()
  const del = useDeleteProject()
  const navigate = useNavigate()
  const [confirmOpen, setConfirmOpen] = useState(false)
  const t = useT()

  if (loading) {
    return <div className="h-40 rounded-lg bg-muted animate-pulse" />
  }

  const canDownload = project.status === 'COMPLETED' && project.output_paths.length > 0

  return (
    <>
      <Card>
        <CardContent className="pt-4 pb-2 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <p className="font-medium text-sm truncate">{project.name || project.input_filename}</p>
            <span className={cn('shrink-0 rounded-full px-2 py-0.5 text-xs font-medium', STATUS_COLOURS[project.status] ?? STATUS_COLOURS.CANCELLED)}>
              {project.status}
            </span>
          </div>
          <dl className="grid grid-cols-2 gap-y-1 text-xs text-muted-foreground">
            <div><dt className="sr-only">Template</dt><dd>{project.template}</dd></div>
            <div><dt className="sr-only">Language</dt><dd>{project.language}</dd></div>
            <div><dt className="sr-only">AI model</dt><dd>{project.ai_model}</dd></div>
            <div><dt className="sr-only">Created</dt><dd>{new Date(project.created_at).toLocaleDateString()}</dd></div>
          </dl>
          {project.output_paths.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {project.output_paths.map((p) => {
                const ext = p.split('.').pop()?.toUpperCase() ?? 'FILE'
                return (
                  <span key={p} className="rounded border px-1.5 py-0.5 text-xs">{ext}</span>
                )
              })}
            </div>
          )}
        </CardContent>

        <CardFooter className="flex gap-2 pb-3 flex-wrap">
          {canDownload && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => void downloadJob(project.job_id, project.output_paths[0].split('.').pop() ?? 'docx')}
              aria-label={`${t.projects.download} ${project.name}`}
            >
              <Download className="h-3.5 w-3.5" />
              {t.projects.download}
            </Button>
          )}

          <Button
            size="sm"
            variant="ghost"
            disabled={duplicate.isPending}
            onClick={() => duplicate.mutate(project.id)}
            aria-label={`${t.projects.duplicate} ${project.name}`}
          >
            {duplicate.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Copy className="h-3.5 w-3.5" />}
            {t.projects.duplicate}
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => navigate(`/projects/${project.id}`)}
            aria-label={`${t.projects.open} ${project.name}`}
          >
            <ExternalLink className="h-3.5 w-3.5" />
            {t.projects.open}
          </Button>

          <Button
            size="sm"
            variant="ghost"
            className="text-destructive hover:text-destructive"
            disabled={del.isPending}
            onClick={() => setConfirmOpen(true)}
            aria-label={`${t.projects.delete} ${project.name}`}
          >
            {del.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
            {t.projects.delete}
          </Button>
        </CardFooter>
      </Card>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.projects.deleteTitle}</DialogTitle>
            <DialogDescription
              dangerouslySetInnerHTML={{
                __html: t.projects.deleteDescription(`<strong>${project.name || project.input_filename}</strong>`),
              }}
            />
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>{t.projects.cancel}</Button>
            <Button
              variant="destructive"
              disabled={del.isPending}
              onClick={() => {
                del.mutate(project.id, { onSuccess: () => setConfirmOpen(false) })
              }}
            >
              {del.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : t.projects.delete}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
