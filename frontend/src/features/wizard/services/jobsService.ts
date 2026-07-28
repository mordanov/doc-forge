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

export async function downloadJob(jobId: string, fmt: string): Promise<void> {
  const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const url = `${base}/jobs/${jobId}/download/${fmt}`

  let token: string | null = null
  try {
    const raw = localStorage.getItem('auth')
    if (raw) {
      const parsed = JSON.parse(raw) as { state?: { token?: string }; token?: string }
      token = parsed.state?.token ?? parsed.token ?? null
    }
  } catch {
    // ignore
  }

  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error(`Download failed: ${res.status}`)

  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = `${jobId}.${fmt}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(objectUrl)
}
