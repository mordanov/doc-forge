import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressTimeline } from '@/components/ProgressTimeline'
import { FileText, Cpu, CheckCircle } from 'lucide-react'
import type { ProgressStage } from '@/components/ProgressTimeline'

const stages: ProgressStage[] = [
  { id: 'upload', label: 'Uploading', icon: FileText, status: 'complete' },
  { id: 'process', label: 'Processing', icon: Cpu, status: 'active', progress: 50 },
  { id: 'finish', label: 'Finishing', icon: CheckCircle, status: 'pending' },
]

describe('ProgressTimeline', () => {
  it('renders all stage labels', () => {
    render(<ProgressTimeline stages={stages} currentStage="process" />)
    expect(screen.getByText('Uploading')).toBeInTheDocument()
    expect(screen.getByText('Processing')).toBeInTheDocument()
    expect(screen.getByText('Finishing')).toBeInTheDocument()
  })

  it('shows progressbar for active stage with progress', () => {
    render(<ProgressTimeline stages={stages} currentStage="process" />)
    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveAttribute('aria-valuenow', '50')
  })

  it('does not show progressbar for non-active stages', () => {
    const noProgress = stages.map((s) => ({ ...s, progress: 50 }))
    render(<ProgressTimeline stages={noProgress.filter((s) => s.status !== 'active')} currentStage="" />)
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
  })

  it('aria-label reflects status', () => {
    render(<ProgressTimeline stages={stages} currentStage="process" />)
    expect(screen.getByLabelText(/uploading: complete/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/processing: active/i)).toBeInTheDocument()
  })
})
