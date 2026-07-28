import { useWizardStore } from '../wizardStore'
import { useEstimate } from '../services/hooks/useEstimate'
import { useSubmitJob } from '../services/hooks/useSubmitJob'
import { WizardNav } from '@/components/WizardNav'
import { CostCard } from '@/components/CostCard'
import { AlertTriangle, CheckCircle } from 'lucide-react'
import { useT } from '@/hooks/useT'

export function Step4Preview() {
  const { draft, goBack } = useWizardStore()
  const estimate = useEstimate()
  const submitJob = useSubmitJob()
  const t = useT()

  function handleGenerate() {
    if (!draft.documentId) return
    submitJob.mutate({
      document_id: draft.documentId,
      template: draft.template,
      language: draft.language,
      ai_model: draft.aiModel,
      creativity: draft.creativity,
      config: {
        output_formats: [draft.outputFormat],
        image_policy: draft.imagePolicy,
        image_sources: [draft.imageSource],
        image_density: draft.imageDensity,
        layout_density: draft.layoutDensity,
        typography: draft.typography,
        colour_palette: draft.colourPalette,
        sidebar_style: draft.sidebarStyle,
        cover_page: draft.coverPage,
        table_of_contents: draft.tableOfContents,
        headers_footers: draft.headersFooters,
        validation_level: draft.validationLevel,
        offline_mode: draft.offlineMode,
      },
    })
  }

  const est = estimate.data

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t.step4.title}</h2>
        <p className="text-sm text-muted-foreground">{t.step4.subtitle}</p>
      </div>

      <CostCard estimate={est!} loading={estimate.isLoading} />

      {est && est.validation_summary.warnings.length > 0 && (
        <div className="rounded-lg border border-yellow-400/50 bg-yellow-50 dark:bg-yellow-900/20 p-4 space-y-2">
          <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
            <AlertTriangle className="h-4 w-4" />
            <p className="text-sm font-medium">{t.step4.warnings(est.validation_summary.warnings.length)}</p>
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
          {t.step4.validationPassed}
        </div>
      )}

      {est && (
        <div className="rounded-lg border p-4 bg-muted/30 text-sm space-y-2">
          <p className="font-medium">{t.step4.licenceSummary}</p>
          <p className="text-muted-foreground text-xs">
            {t.step4.licensed(est.licence_summary.expected_licensed, est.licence_summary.providers_available.join(', '))}
            {est.licence_summary.expected_unlicensed > 0 && t.step4.unlicensed(est.licence_summary.expected_unlicensed)}
          </p>
        </div>
      )}

      {submitJob.error && (
        <p className="text-sm text-destructive">{t.step4.generateFailed}</p>
      )}

      <WizardNav
        currentStep={4}
        onBack={goBack}
        onNext={handleGenerate}
        nextLabel={t.step4.generate}
        nextDisabled={!est || submitJob.isPending}
        nextLoading={submitJob.isPending}
      />
    </div>
  )
}
