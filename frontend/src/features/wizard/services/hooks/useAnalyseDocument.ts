import { useQuery } from '@tanstack/react-query'
import { analyseDocument } from '../documentsService'
import { useWizardStore } from '../../wizardStore'

export function useAnalyseDocument(docId: string | null) {
  const setDocument = useWizardStore((s) => s.setDocument)
  const draft = useWizardStore((s) => s.draft)

  return useQuery({
    queryKey: ['analyse', docId],
    queryFn: async () => {
      const analysis = await analyseDocument(docId!)
      setDocument({ id: docId!, filename: draft.filename!, size: 0 }, analysis)
      return analysis
    },
    enabled: docId != null,
    staleTime: Infinity,
  })
}
