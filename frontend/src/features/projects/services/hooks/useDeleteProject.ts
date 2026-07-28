import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteProject } from '../projectsService'

export function useDeleteProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteProject(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['projects'] }),
  })
}
