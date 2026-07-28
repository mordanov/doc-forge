import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import type { HealthCheck } from '@/types/api'
import { ExternalLink } from 'lucide-react'
import { useT } from '@/hooks/useT'

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
  const t = useT()

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold">{t.about.title}</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Version {health?.version ?? APP_VERSION}
        </p>
      </div>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">{t.about.whatTitle}</h2>
        <p className="text-sm text-muted-foreground">{t.about.whatBody}</p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold">{t.about.linksTitle}</h2>
        <div className="flex flex-col gap-2">
          <a
            href="https://github.com/docforge/docforge"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:underline w-fit"
            aria-label={`${t.about.github} (opens in new tab)`}
          >
            {t.about.github}
            <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href="https://github.com/docforge/docforge/wiki"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:underline w-fit"
            aria-label={`${t.about.docs} (opens in new tab)`}
          >
            <ExternalLink className="h-4 w-4" />
            {t.about.docs}
          </a>
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">{t.about.contributorsTitle}</h2>
        <p className="text-sm text-muted-foreground">{t.about.contributorsBody}</p>
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">{t.about.licenceTitle}</h2>
        <p className="text-sm text-muted-foreground">
          {t.about.licenceBody}{' '}
          <a
            href="https://opensource.org/licenses/MIT"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {t.about.licenceName}
          </a>
          {t.about.licenceTrail}
        </p>
      </section>
    </div>
  )
}
