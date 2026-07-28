import api from '@/lib/api'
import type { Project, ParsedProject, JobSubmitResponse } from '@/types/api'
import { parseProject } from '@/lib/utils'

export async function getProjects(params?: { offset?: number; limit?: number }): Promise<ParsedProject[]> {
  const { data } = await api.get<Project[]>('/projects', { params })
  return data.map(parseProject)
}

export async function getProject(id: string): Promise<ParsedProject> {
  const { data } = await api.get<Project>(`/projects/${id}`)
  return parseProject(data)
}

export async function duplicateProject(id: string): Promise<JobSubmitResponse> {
  const { data } = await api.post<JobSubmitResponse>(`/projects/${id}/duplicate`)
  return data
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`)
}
