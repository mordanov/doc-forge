import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import type { HealthCheck } from '@/types/api'
import { ExternalLink, Github } from 'lucide-react'

const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? '0.1.0'

function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await api.get<HealthCheck>('/system/health')
      return data
    },
    retry: 1,
  })
}

export default function AboutPage() {
  const { data: health } = useHealth()

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold">About DocForge</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Version {health?.version ?? APP_VERSION}
        </p>
      </div>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">What is DocForge?</h2>
        <p className="text-sm text-muted-foreground">
          DocForge transforms Word documents into beautifully formatted publications using AI.
          Upload a .docx file, configure AI and publication settings, and download a polished output.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold">Links</h2>
        <div className="flex flex-col gap-2">
          <a
            href="https://github.com/docforge/docforge"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:underline w-fit"
            aria-label="GitHub repository (opens in new tab)"
          >
            <Github className="h-4 w-4" />
            GitHub Repository
            <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href="https://github.com/docforge/docforge/wiki"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:underline w-fit"
            aria-label="Documentation (opens in new tab)"
          >
            <ExternalLink className="h-4 w-4" />
            Documentation
          </a>
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">Contributors</h2>
        <p className="text-sm text-muted-foreground">
          DocForge is an open-source project. See the GitHub repository for a full list of contributors.
        </p>
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">Licence</h2>
        <p className="text-sm text-muted-foreground">
          DocForge is released under the{' '}
          <a
            href="https://opensource.org/licenses/MIT"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            MIT Licence
          </a>
          . You are free to use, modify, and distribute this software in accordance with its terms.
        </p>
      </section>
    </div>
  )
}
