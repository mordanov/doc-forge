import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface StatisticsCardProps {
  label: string
  value: number | string
  unit?: string
  icon?: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
}

export function StatisticsCard({ label, value, unit, icon: Icon, trend }: StatisticsCardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus

  return (
    <Card>
      <CardContent className="pt-4 pb-3">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="text-2xl font-bold mt-1">
              {value}
              {unit && <span className="text-sm font-normal text-muted-foreground ml-1">{unit}</span>}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
            {trend && (
              <TrendIcon className={cn('h-4 w-4', trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-muted-foreground')} />
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
