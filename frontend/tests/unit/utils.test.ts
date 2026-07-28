import { describe, it, expect } from 'vitest'
import { parseJob, parseProject, formatBytes, formatDuration } from '@/lib/utils'
import type { Job, Project } from '@/types/api'

const baseJob: Job = {
  id: 'j1',
  project_id: null,
  status: 'COMPLETED',
  stage: 'FINISHED',
  progress: 100,
  elapsed_seconds: 42,
  config_snapshot: '{}',
  input_filename: 'doc.docx',
  input_path: '/tmp/doc.docx',
  output_paths: '["output/doc.docx","output/doc.pdf"]',
  warnings: '["warn1","warn2"]',
  error: null,
  created_at: '2026-07-27T00:00:00Z',
  started_at: null,
  completed_at: null,
}

describe('parseJob', () => {
  it('parses output_paths from JSON string', () => {
    const parsed = parseJob(baseJob)
    expect(parsed.output_paths).toEqual(['output/doc.docx', 'output/doc.pdf'])
  })

  it('parses warnings from JSON string', () => {
    const parsed = parseJob(baseJob)
    expect(parsed.warnings).toEqual(['warn1', 'warn2'])
  })

  it('returns empty arrays for empty JSON strings', () => {
    const parsed = parseJob({ ...baseJob, output_paths: '[]', warnings: '[]' })
    expect(parsed.output_paths).toEqual([])
    expect(parsed.warnings).toEqual([])
  })

  it('handles missing/null-ish JSON gracefully', () => {
    const parsed = parseJob({ ...baseJob, output_paths: '', warnings: '' })
    expect(parsed.output_paths).toEqual([])
    expect(parsed.warnings).toEqual([])
  })
})

const baseProject: Project = {
  id: 'p1',
  name: 'Test',
  job_id: 'j1',
  input_filename: 'doc.docx',
  config_snapshot: '{"key":"val"}',
  output_paths: '["output/doc.docx"]',
  template: 'minimal',
  language: 'en',
  ai_model: 'gpt-4o',
  status: 'COMPLETED',
  created_at: '2026-07-27T00:00:00Z',
  completed_at: null,
}

describe('parseProject', () => {
  it('parses output_paths', () => {
    expect(parseProject(baseProject).output_paths).toEqual(['output/doc.docx'])
  })

  it('parses config_snapshot', () => {
    expect(parseProject(baseProject).config_snapshot).toEqual({ key: 'val' })
  })
})

describe('formatBytes', () => {
  it('formats 0', () => expect(formatBytes(0)).toBe('0 B'))
  it('formats KB', () => expect(formatBytes(1024)).toBe('1 KB'))
  it('formats MB', () => expect(formatBytes(1024 * 1024)).toBe('1 MB'))
})

describe('formatDuration', () => {
  it('formats seconds', () => expect(formatDuration(45)).toBe('45s'))
  it('formats minutes', () => expect(formatDuration(90)).toBe('1m 30s'))
  it('formats exact minutes', () => expect(formatDuration(120)).toBe('2m'))
})
