import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { Job, ParsedJob, Project, ParsedProject } from '@/types/api'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parseJob(raw: Job): ParsedJob {
  return {
    ...raw,
    output_paths: JSON.parse(raw.output_paths || '[]') as string[],
    warnings: JSON.parse(raw.warnings || '[]') as string[],
  }
}

export function parseProject(raw: Project): ParsedProject {
  return {
    ...raw,
    output_paths: JSON.parse(raw.output_paths || '[]') as string[],
    config_snapshot: JSON.parse(raw.config_snapshot || '{}') as Record<string, unknown>,
  }
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return s > 0 ? `${m}m ${s}s` : `${m}m`
}
