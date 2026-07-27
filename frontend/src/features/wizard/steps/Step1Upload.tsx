import { useState } from 'react'
import { UploadArea } from '@/components/UploadArea'
import { WizardNav } from '@/components/WizardNav'
import { useWizardStore } from '../wizardStore'
import { useUploadDocument } from '../services/hooks/useUploadDocument'
import { useAnalyseDocument } from '../services/hooks/useAnalyseDocument'
import { formatBytes } from '@/lib/utils'

export function Step1Upload() {
  const { draft, goNext } = useWizardStore()
  const upload = useUploadDocument()
  const analyse = useAnalyseDocument(draft.documentId)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const isLoading = upload.isPending || analyse.isLoading
  const hasDoc = draft.documentId != null && draft.analysis != null
  const stats = draft.analysis?.statistics

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Upload Document</h2>
        <p className="text-sm text-muted-foreground">Select a .docx file to begin</p>
      </div>

      {!hasDoc ? (
        <>
          <UploadArea
            onFile={(file) => { setUploadError(null); upload.mutate(file) }}
            onError={setUploadError}
            disabled={isLoading}
          />
          {(uploadError || upload.error || analyse.error) && (
            <p className="text-sm text-destructive">
              {uploadError ?? 'Upload failed. Please try again.'}
            </p>
          )}
          {isLoading && (
            <p className="text-sm text-muted-foreground animate-pulse">
              {upload.isPending ? 'Uploading…' : 'Analysing document…'}
            </p>
          )}
        </>
      ) : (
        <div className="rounded-lg border p-4 bg-muted/40 space-y-3">
          <div className="flex items-center justify-between">
            <p className="font-medium text-sm">{draft.filename}</p>
            <button
              type="button"
              onClick={() => useWizardStore.getState().reset()}
              className="text-xs text-muted-foreground hover:text-foreground"
              aria-label="Remove document and start over"
            >
              Remove
            </button>
          </div>
          {stats && (
            <dl className="grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4 text-sm">
              {[
                ['Pages', stats.estimated_pages],
                ['Headings', stats.headings],
                ['Tables', stats.tables],
                ['Images', stats.image_placeholders],
                ['Words', stats.words.toLocaleString()],
                ['Chapters', stats.chapters],
              ].map(([label, val]) => (
                <div key={String(label)}>
                  <dt className="text-xs text-muted-foreground">{label}</dt>
                  <dd className="font-medium">{val}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}

      <WizardNav
        currentStep={1}
        onNext={hasDoc ? goNext : undefined}
        nextDisabled={!hasDoc}
      />
    </div>
  )
}
