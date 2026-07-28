import { useQuery } from '@tanstack/react-query'
import { getProjects } from '../projectsService'

interface UseProjectsParams {
  offset?: number
  limit?: number
}

export function useProjects(params: UseProjectsParams = {}) {
  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => getProjects(params),
  })
}
