import { useEffect, useState } from 'react'
import { useWizardStore } from './wizardStore'
import { useDefaultsForWizard } from '@/features/settings/settingsStore'
import { Step1Upload } from './steps/Step1Upload'
import { Step2AiConfig } from './steps/Step2AiConfig'
import { Step3PublicationConfig } from './steps/Step3PublicationConfig'
import { Step4Preview } from './steps/Step4Preview'
import { Step5Rendering } from './steps/Step5Rendering'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useT } from '@/hooks/useT'

const STEP_COMPONENTS = {
  1: Step1Upload,
  2: Step2AiConfig,
  3: Step3PublicationConfig,
  4: Step4Preview,
  5: Step5Rendering,
} as const

export default function NewProjectWizard() {
  const { draft, hasSavedDraft, reset, setPublicationConfig } = useWizardStore()
  const settingsDefaults = useDefaultsForWizard()
  const [promptShown, setPromptShown] = useState(false)
  const [promptResolved, setPromptResolved] = useState(false)
  const t = useT()

  useEffect(() => {
    if (hasSavedDraft && draft.documentId && !promptResolved) {
      setPromptShown(true)
    } else {
      setPublicationConfig({
        language: settingsDefaults.language,
        template: settingsDefaults.template,
        outputFormat: settingsDefaults.outputFormat,
      })
      setPromptResolved(true)
    }
  }, []) // run once on mount

  function handleContinue() {
    setPromptShown(false)
    setPromptResolved(true)
  }

  function handleStartFresh() {
    reset()
    setPublicationConfig({
      language: settingsDefaults.language,
      template: settingsDefaults.template,
      outputFormat: settingsDefaults.outputFormat,
    })
    setPromptShown(false)
    setPromptResolved(true)
  }

  const StepComponent = STEP_COMPONENTS[draft.step] ?? Step1Upload

  return (
    <>
      <Dialog open={promptShown} onOpenChange={() => {}}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.wizardResume.title}</DialogTitle>
            <DialogDescription>
              {t.wizardResume.description(draft.filename ?? 'untitled')}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleStartFresh}>{t.wizardResume.startFresh}</Button>
            <Button onClick={handleContinue}>{t.wizardResume.continue}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {promptResolved && (
        <div className="max-w-3xl mx-auto p-6">
          <ErrorBoundary>
            <StepComponent />
          </ErrorBoundary>
        </div>
      )}
    </>
  )
}
