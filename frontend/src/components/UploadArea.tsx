import { useRef, useState, type DragEvent, type ChangeEvent } from 'react'
import { Upload } from 'lucide-react'
import { cn } from '@/lib/utils'

interface UploadAreaProps {
  onFile: (file: File) => void
  onError: (message: string) => void
  accept?: string[]
  maxSizeBytes?: number
  disabled?: boolean
  children?: React.ReactNode
}

const DEFAULT_ACCEPT = ['.docx']
const DEFAULT_MAX = 50 * 1024 * 1024

export function UploadArea({
  onFile,
  onError,
  accept = DEFAULT_ACCEPT,
  maxSizeBytes = DEFAULT_MAX,
  disabled = false,
  children,
}: UploadAreaProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function validate(file: File): string | null {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!accept.includes(ext)) {
      return `Only ${accept.join(', ')} files are accepted`
    }
    if (file.size > maxSizeBytes) {
      return `File exceeds the ${Math.round(maxSizeBytes / 1024 / 1024)} MB limit`
    }
    return null
  }

  function handleFile(file: File) {
    const err = validate(file)
    if (err) { onError(err); return }
    onFile(file)
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload document"
      aria-disabled={disabled}
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-12 transition-colors cursor-pointer',
        dragging ? 'border-primary bg-accent' : 'border-muted-foreground/30 hover:border-primary hover:bg-accent/50',
        disabled && 'pointer-events-none opacity-50'
      )}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inputRef.current?.click() } }}
    >
      <Upload className="h-10 w-10 text-muted-foreground" />
      {children ?? (
        <>
          <p className="text-sm font-medium">Drag & drop your .docx file here</p>
          <p className="text-xs text-muted-foreground">or click to browse — max {Math.round(maxSizeBytes / 1024 / 1024)} MB</p>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={accept.join(',')}
        className="sr-only"
        onChange={onChange}
        tabIndex={-1}
      />
    </div>
  )
}
