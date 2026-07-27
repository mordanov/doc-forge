import { useWizardStore } from '../wizardStore'
import { useEstimate } from '../services/hooks/useEstimate'
import { useSubmitJob } from '../services/hooks/useSubmitJob'
import { WizardNav } from '@/components/WizardNav'
import { CostCard } from '@/components/CostCard'
import { AlertTriangle, CheckCircle } from 'lucide-react'

export function Step4Preview() {
  const { draft, goBack } = useWizardStore()
  const estimate = useEstimate()
  const submitJob = useSubmitJob()

  function handleGenerate() {
    if (!draft.documentId) return
    submitJob.mutate({
      document_id: draft.documentId,
      template: draft.template,
      language: draft.language,
      ai_model: draft.aiModel,
      creativity: draft.creativity,
      config: {
        output_formats: draft.outputFormats,
        image_policy: draft.imagePolicy,
        image_density: draft.imageDensity,
        layout_density: draft.layoutDensity,
        validation_level: draft.validationLevel,
        offline_mode: draft.offlineMode,
      },
    })
  }

  const est = estimate.data

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Preview</h2>
        <p className="text-sm text-muted-foreground">Review the estimate before generating</p>
      </div>

      <CostCard estimate={est!} loading={estimate.isLoading} />

      {est && est.validation_summary.warnings.length > 0 && (
        <div className="rounded-lg border border-yellow-400/50 bg-yellow-50 dark:bg-yellow-900/20 p-4 space-y-2">
          <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
            <AlertTriangle className="h-4 w-4" />
            <p className="text-sm font-medium">Warnings ({est.validation_summary.warnings.length})</p>
          </div>
          <ul className="space-y-1">
            {est.validation_summary.warnings.map((w, i) => (
              <li key={i} className="text-xs text-yellow-700 dark:text-yellow-300">{w}</li>
            ))}
          </ul>
        </div>
      )}

      {est && est.validation_summary.errors.length === 0 && (
        <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm">
          <CheckCircle className="h-4 w-4" />
          Validation passed — no errors found
        </div>
      )}

      {est && (
        <div className="rounded-lg border p-4 bg-muted/30 text-sm space-y-2">
          <p className="font-medium">Licence Summary</p>
          <p className="text-muted-foreground text-xs">
            {est.licence_summary.expected_licensed} licensed image(s) from {est.licence_summary.providers_available.join(', ')}
            {est.licence_summary.expected_unlicensed > 0 && `, ${est.licence_summary.expected_unlicensed} may require attribution`}
          </p>
        </div>
      )}

      {submitJob.error && (
        <p className="text-sm text-destructive">Failed to start job. Please try again.</p>
      )}

      <WizardNav
        currentStep={4}
        onBack={goBack}
        onNext={handleGenerate}
        nextLabel="Generate"
        nextDisabled={!est || submitJob.isPending}
        nextLoading={submitJob.isPending}
      />
    </div>
  )
}
