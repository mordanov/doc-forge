import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjects } from './services/hooks/useProjects'
import { ProjectCard } from './ProjectCard'
import { Button } from '@/components/ui/button'
import { FilePlus, FolderOpen } from 'lucide-react'
import { useT } from '@/hooks/useT'

const PAGE_SIZE = 20

export default function ProjectsPage() {
  const [page, setPage] = useState(1)
  const navigate = useNavigate()
  const t = useT()
  const { data: projects, isLoading } = useProjects({
    offset: (page - 1) * PAGE_SIZE,
    limit: PAGE_SIZE,
  })

  const totalPages = projects ? Math.ceil(projects.length === PAGE_SIZE ? page + 1 : page) : 1

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t.projects.title}</h1>
        <Button onClick={() => navigate('/projects/new')}>
          <FilePlus className="h-4 w-4" />
          {t.projects.newProject}
        </Button>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {!isLoading && projects && projects.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 gap-4 text-muted-foreground">
          <FolderOpen className="h-12 w-12 opacity-30" />
          <p className="text-sm">{t.projects.noProjects}</p>
          <Button onClick={() => navigate('/projects/new')}>
            <FilePlus className="h-4 w-4" />
            {t.projects.createPublication}
          </Button>
        </div>
      )}

      {!isLoading && projects && projects.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            {t.projects.previous}
          </Button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <Button
              key={p}
              variant={p === page ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPage(p)}
              aria-current={p === page ? 'page' : undefined}
            >
              {p}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            {t.projects.next}
          </Button>
        </div>
      )}
    </div>
  )
}
