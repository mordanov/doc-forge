import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { UploadArea } from '@/components/UploadArea'
import { useUploadDocument } from '@/features/wizard/services/hooks/useUploadDocument'
import { useWizardStore } from '@/features/wizard/wizardStore'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FolderOpen, Plus } from 'lucide-react'
import api from '@/lib/api'
import type { Project } from '@/types/api'
import { parseProject } from '@/lib/utils'
import { useT } from '@/hooks/useT'

function useRecentProjects() {
  return useQuery({
    queryKey: ['projects', { limit: 3 }],
    queryFn: async () => {
      const { data } = await api.get<Project[]>('/projects', { params: { limit: 3 } })
      return data.map(parseProject)
    },
  })
}

function ProjectCardSkeleton() {
  return <div className="h-24 rounded-lg bg-muted animate-pulse" />
}

export default function HomePage() {
  const navigate = useNavigate()
  const upload = useUploadDocument()
  const { setDocument } = useWizardStore()
  const recent = useRecentProjects()
  const [uploadError, setUploadError] = useState<string | null>(null)
  const t = useT()

  function handleFile(file: File) {
    setUploadError(null)
    upload.mutate(file, {
      onSuccess: (doc) => {
        setDocument(doc, null)
        navigate('/projects/new')
      },
    })
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-10">
      <section className="space-y-4">
        <h1 className="text-3xl font-bold">{t.appName}</h1>
        <p className="text-muted-foreground">{t.home.tagline}</p>
        <UploadArea
          onFile={handleFile}
          onError={setUploadError}
          disabled={upload.isPending}
        />
        {uploadError && <p className="text-sm text-destructive">{uploadError}</p>}
        {upload.isPending && <p className="text-sm text-muted-foreground animate-pulse">{t.home.uploading}</p>}
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">{t.home.recentProjects}</h2>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/projects/new')}>
              <Plus className="h-4 w-4" />
              {t.home.newBtn}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => navigate('/projects')}>
              <FolderOpen className="h-4 w-4" />
              {t.home.browseAll}
            </Button>
          </div>
        </div>

        {recent.isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {Array.from({ length: 3 }).map((_, i) => <ProjectCardSkeleton key={i} />)}
          </div>
        )}

        {recent.data && recent.data.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground text-sm">
              {t.home.noProjects}
            </CardContent>
          </Card>
        )}

        {recent.data && recent.data.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {recent.data.map((project) => (
              <Card key={project.id} className="hover:shadow-sm transition-shadow">
                <CardContent className="pt-4 pb-3">
                  <p className="font-medium text-sm truncate">{project.name || project.input_filename}</p>
                  <p className="text-xs text-muted-foreground mt-1">{project.template} · {project.status}</p>
                  <p className="text-xs text-muted-foreground">{new Date(project.created_at).toLocaleDateString()}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
