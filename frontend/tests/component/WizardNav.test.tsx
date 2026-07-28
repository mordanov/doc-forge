import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { WizardNav } from '@/components/WizardNav'

describe('WizardNav', () => {
  it('shows all 5 step indicators', () => {
    render(<WizardNav currentStep={1} />)
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByLabelText(new RegExp(`Step ${i}`))).toBeInTheDocument()
    }
  })

  it('Back button hidden on step 1', () => {
    render(<WizardNav currentStep={1} onBack={vi.fn()} />)
    expect(screen.getByRole('button', { name: /back/i })).toHaveClass('invisible')
  })

  it('Back button visible on step 2+', () => {
    render(<WizardNav currentStep={2} onBack={vi.fn()} />)
    expect(screen.getByRole('button', { name: /back/i })).not.toHaveClass('invisible')
  })

  it('calls onNext when Next clicked', async () => {
    const onNext = vi.fn()
    render(<WizardNav currentStep={1} onNext={onNext} />)
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(onNext).toHaveBeenCalled()
  })

  it('Next button disabled when nextDisabled', () => {
    render(<WizardNav currentStep={1} onNext={vi.fn()} nextDisabled />)
    expect(screen.getByRole('button', { name: /next/i })).toBeDisabled()
  })

  it('shows custom nextLabel', () => {
    render(<WizardNav currentStep={1} onNext={vi.fn()} nextLabel="Submit" />)
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument()
  })
})
