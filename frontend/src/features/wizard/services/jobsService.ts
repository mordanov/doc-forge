import api from '@/lib/api'
import type { JobSubmitRequest, JobSubmitResponse, Job, JobEstimate, ParsedJob } from '@/types/api'
import { parseJob } from '@/lib/utils'

export async function submitJob(req: JobSubmitRequest): Promise<JobSubmitResponse> {
  const { data } = await api.post<JobSubmitResponse>('/jobs', req)
  return data
}

export async function getJob(id: string): Promise<ParsedJob> {
  const { data } = await api.get<Job>(`/jobs/${id}`)
  return parseJob(data)
}

export async function getEstimate(req: JobSubmitRequest): Promise<JobEstimate> {
  const { data } = await api.post<JobEstimate>('/jobs/estimate', req)
  return data
}

export function downloadJob(jobId: string, fmt: string): void {
  const url = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/jobs/${jobId}/download/${fmt}`
  const a = document.createElement('a')
  a.href = url
  a.download = ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
