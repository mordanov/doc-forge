import { useMutation, useQueryClient } from '@tanstack/react-query'
import { submitJob } from '../jobsService'
import { useWizardStore } from '../../wizardStore'
import type { JobSubmitRequest } from '@/types/api'

export function useSubmitJob() {
  const setActiveJob = useWizardStore((s) => s.setActiveJob)
  const goNext = useWizardStore((s) => s.goNext)
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (req: JobSubmitRequest) => submitJob(req),
    onSuccess: (res) => {
      setActiveJob(res.job_id)
      goNext()
      void qc.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}
