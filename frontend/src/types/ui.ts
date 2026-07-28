import type { DocumentAnalysis, JobEstimate } from './api'

export type WizardStep = 1 | 2 | 3 | 4 | 5

export type OutputFormat = 'docx' | 'pdf' | 'html' | 'markdown' | 'epub'
export type ImagePolicy = 'auto' | 'placeholders_only' | 'preserve' | 'disable'

export interface WizardDraft {
  step: WizardStep
  documentId: string | null
  filename: string | null
  analysis: DocumentAnalysis | null
  aiProvider: 'openai'
  aiModel: string
  aiQuality: 'fast' | 'balanced' | 'maximum'
  creativity: number
  presetId: string | null
  template: string
  outputFormat: OutputFormat
  language: string
  imagePolicy: ImagePolicy
  imageSource: string
  imageDensity: 'minimal' | 'balanced' | 'illustrated' | 'maximum'
  layoutDensity: 'compact' | 'balanced' | 'spacious'
  typography: string
  colourPalette: string
  customColour: string | null
  sidebarStyle: string
  coverPage: string
  tableOfContents: string
  headersFooters: string
  validationLevel: 'fast' | 'standard' | 'strict'
  aiExplainability: 'off' | 'brief' | 'detailed'
  offlineMode: boolean
  promptVersion: string | null
  themeVersion: string | null
  parallelDownloads: number
  retryCount: number
  timeout: number
  cacheLocation: string | null
  cacheSize: number | null
  maxAiRequests: number | null
  estimate: JobEstimate | null
  activeJobId: string | null
}

export interface Preset {
  id: string
  name: string
  description: string
  config: Partial<WizardDraft>
}

export interface AppSettings {
  theme: 'light' | 'dark'
  defaultLanguage: string
  defaultOutputFormat: OutputFormat
  defaultTemplate: string
  openAiApiKey: string | null
}
