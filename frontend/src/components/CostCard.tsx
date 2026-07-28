import type { JobEstimate } from '@/types/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { StatisticsCard } from './StatisticsCard'
import { Clock, Brain, Image, FileText, DollarSign, BookOpen, ListOrdered, LayoutTemplate, MessageSquare } from 'lucide-react'
import { formatDuration } from '@/lib/utils'
import { useT } from '@/hooks/useT'

interface CostCardProps {
  estimate: JobEstimate
  loading?: boolean
}

export function CostCard({ estimate, loading }: CostCardProps) {
  const t = useT()

  if (loading) {
    return <div className="h-48 rounded-lg bg-muted animate-pulse" />
  }

  const costLabel = estimate.estimated_ai_cost_usd < 0.01
    ? '< $0.01'
    : `$${estimate.estimated_ai_cost_usd.toFixed(2)}`

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Estimate</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatisticsCard
          label="Render time"
          value={formatDuration(estimate.estimated_rendering_seconds)}
          icon={Clock}
        />
        <StatisticsCard
          label="AI tokens"
          value={estimate.estimated_ai_tokens.toLocaleString()}
          icon={Brain}
        />
        <StatisticsCard
          label={t.step4.estimatedCost}
          value={costLabel}
          icon={DollarSign}
        />
        <StatisticsCard
          label="AI requests"
          value={estimate.estimated_ai_requests}
          icon={Brain}
        />
        <StatisticsCard
          label="Images"
          value={estimate.image_placeholder_count}
          icon={Image}
        />
        <StatisticsCard
          label="Pages"
          value={estimate.estimated_page_count}
          icon={FileText}
        />
        <StatisticsCard
          label="Captions"
          value={estimate.generated_captions}
          icon={MessageSquare}
        />
        <StatisticsCard
          label="Appendix"
          value={estimate.generated_appendix ? 'Yes' : 'No'}
          icon={BookOpen}
        />
        <StatisticsCard
          label="Cover page"
          value={estimate.has_cover_page ? 'Yes' : 'No'}
          icon={LayoutTemplate}
        />
        <StatisticsCard
          label="Table of contents"
          value={estimate.has_toc ? 'Yes' : 'No'}
          icon={ListOrdered}
        />
      </CardContent>
    </Card>
  )
}
