import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { UploadArea } from '@/components/UploadArea'

function makeFile(name: string, size = 100, type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
  return new File(['x'.repeat(size)], name, { type })
}

describe('UploadArea', () => {
  it('renders upload button', () => {
    render(<UploadArea onFile={vi.fn()} onError={vi.fn()} />)
    expect(screen.getByRole('button', { name: /upload document/i })).toBeInTheDocument()
  })

  it('calls onFile with valid .docx', () => {
    const onFile = vi.fn()
    render(<UploadArea onFile={onFile} onError={vi.fn()} />)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const file = makeFile('doc.docx')
    fireEvent.change(input, { target: { files: [file] } })
    expect(onFile).toHaveBeenCalledWith(file)
  })

  it('calls onError for wrong extension', () => {
    const onError = vi.fn()
    render(<UploadArea onFile={vi.fn()} onError={onError} />)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const file = makeFile('doc.txt')
    fireEvent.change(input, { target: { files: [file] } })
    expect(onError).toHaveBeenCalledWith(expect.stringContaining('.docx'))
  })

  it('calls onError for oversized file', () => {
    const onError = vi.fn()
    render(<UploadArea onFile={vi.fn()} onError={onError} maxSizeBytes={10} />)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const file = makeFile('doc.docx', 100)
    fireEvent.change(input, { target: { files: [file] } })
    expect(onError).toHaveBeenCalledWith(expect.stringContaining('limit'))
  })

  it('is disabled when prop set', () => {
    render(<UploadArea onFile={vi.fn()} onError={vi.fn()} disabled />)
    expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true')
  })
})
