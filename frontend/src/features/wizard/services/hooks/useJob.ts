import { useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { getJob } from '../jobsService'

const TERMINAL = ['COMPLETED', 'FAILED', 'CANCELLED'] as const

interface UseJobOptions {
  pollingInterval?: number
}

export function useJob(jobId: string | null, options: UseJobOptions = {}) {
  const { pollingInterval = 3000 } = options
  const failureCount = useRef(0)

  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      const job = await getJob(jobId!)
      failureCount.current = 0
      return job
    },
    enabled: jobId != null,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data && TERMINAL.includes(data.status as typeof TERMINAL[number])) return false
      return pollingInterval
    },
    staleTime: 0,
  })

  const connectionLost = query.isError && failureCount.current >= 3

  return { ...query, connectionLost }
}
