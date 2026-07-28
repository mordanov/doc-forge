import { useMutation, useQueryClient } from '@tanstack/react-query'
import { duplicateProject } from '../projectsService'

export function useDuplicateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => duplicateProject(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['projects'] }),
  })
}
