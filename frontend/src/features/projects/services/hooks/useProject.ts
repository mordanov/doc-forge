import { useQuery } from '@tanstack/react-query'
import { getProject } from '../projectsService'

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => getProject(id),
    enabled: !!id,
  })
}
