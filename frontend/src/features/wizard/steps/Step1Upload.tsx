import { useState } from 'react'
import { UploadArea } from '@/components/UploadArea'
import { WizardNav } from '@/components/WizardNav'
import { useWizardStore } from '../wizardStore'
import { useUploadDocument } from '../services/hooks/useUploadDocument'
import { useAnalyseDocument } from '../services/hooks/useAnalyseDocument'
import { useT } from '@/hooks/useT'

export function Step1Upload() {
  const { draft, goNext } = useWizardStore()
  const upload = useUploadDocument()
  const analyse = useAnalyseDocument(draft.documentId)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const t = useT()

  const isLoading = upload.isPending || analyse.isLoading
  const hasDoc = draft.documentId != null && draft.analysis != null
  const stats = draft.analysis?.statistics

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t.step1.title}</h2>
        <p className="text-sm text-muted-foreground">{t.step1.subtitle}</p>
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
              {uploadError ?? t.step1.uploadFailed}
            </p>
          )}
          {isLoading && (
            <p className="text-sm text-muted-foreground animate-pulse">
              {upload.isPending ? t.step1.uploading : t.step1.analysing}
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
              {t.step1.remove}
            </button>
          </div>
          {stats && (
            <dl className="grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4 text-sm">
              {[
                [t.step1.stats.pages, stats.estimated_pages],
                [t.step1.stats.headings, stats.headings],
                [t.step1.stats.tables, stats.tables],
                [t.step1.stats.images, stats.image_placeholders],
                [t.step1.stats.words, stats.words.toLocaleString()],
                [t.step1.stats.chapters, stats.chapters],
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
