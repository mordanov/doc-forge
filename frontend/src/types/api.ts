export interface AuthToken {
  access_token: string
  token_type: 'bearer'
}

export interface UploadedDocument {
  id: string
  filename: string
  size: number
}

export interface ValidationIssue {
  code: string
  message: string
  location: string
}

export interface DocumentAnalysis {
  document_id: string
  statistics: {
    chapters: number
    headings: number
    tables: number
    image_placeholders: number
    words: number
    estimated_pages: number
  }
  issues: ValidationIssue[]
}

export type JobStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'

export type RenderStage =
  | 'UPLOADING'
  | 'LOADING'
  | 'ANALYSING'
  | 'AI_PROCESSING'
  | 'IMAGE_SEARCH'
  | 'IMAGE_DOWNLOAD'
  | 'RENDERING'
  | 'VALIDATION'
  | 'EXPORT'
  | 'FINISHED'

export interface Job {
  id: string
  project_id: string | null
  status: JobStatus
  stage: RenderStage
  progress: number
  elapsed_seconds: number
  config_snapshot: string
  input_filename: string
  input_path: string
  output_paths: string
  warnings: string
  error: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface ParsedJob extends Omit<Job, 'output_paths' | 'warnings'> {
  output_paths: string[]
  warnings: string[]
}

export interface JobSubmitRequest {
  document_id: string
  template?: string
  language?: string
  ai_model?: string
  creativity?: number
  config?: Record<string, unknown>
}

export interface JobSubmitResponse {
  job_id: string
  status: 'QUEUED'
}

export interface JobEstimate {
  estimated_rendering_seconds: number
  estimated_ai_tokens: number
  estimated_ai_requests: number
  estimated_page_count: number
  image_placeholder_count: number
  validation_summary: {
    warnings: string[]
    errors: string[]
  }
  licence_summary: {
    providers_available: string[]
    expected_licensed: number
    expected_unlicensed: number
  }
}

export interface Project {
  id: string
  name: string
  job_id: string
  input_filename: string
  config_snapshot: string
  output_paths: string
  template: string
  language: string
  ai_model: string
  status: string
  created_at: string
  completed_at: string | null
}

export interface ParsedProject extends Omit<Project, 'output_paths' | 'config_snapshot'> {
  output_paths: string[]
  config_snapshot: Record<string, unknown>
}

export interface Theme {
  id: string
  version: string
  author: string
  supports_cover: boolean
  supports_sidebars: boolean
}

export interface AIProviderStatus {
  id: string
  available: boolean
  reason?: string
}

export interface ImageProviderStatus {
  id: string
  available: boolean
  requires_key: boolean
}

export interface ProvidersStatus {
  ai: AIProviderStatus[]
  images: ImageProviderStatus[]
}

export interface HealthCheck {
  status: 'ok'
  version: string
}

export interface ApiError {
  detail: string
}
