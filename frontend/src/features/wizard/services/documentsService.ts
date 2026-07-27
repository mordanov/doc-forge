import api from '@/lib/api'
import type { UploadedDocument, DocumentAnalysis } from '@/types/api'

export async function uploadDocument(file: File): Promise<UploadedDocument> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<UploadedDocument>('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function analyseDocument(docId: string): Promise<DocumentAnalysis> {
  const { data } = await api.post<DocumentAnalysis>(`/documents/${docId}/analyse`)
  return data
}
