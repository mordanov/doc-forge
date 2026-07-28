import type { JobEstimate } from '@/types/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { StatisticsCard } from './StatisticsCard'
import { Clock, Brain, Image, FileText } from 'lucide-react'
import { formatDuration } from '@/lib/utils'

interface CostCardProps {
  estimate: JobEstimate
  loading?: boolean
}

export function CostCard({ estimate, loading }: CostCardProps) {
  if (loading) {
    return <div className="h-48 rounded-lg bg-muted animate-pulse" />
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Estimate</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-4">
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
      </CardContent>
    </Card>
  )
}
