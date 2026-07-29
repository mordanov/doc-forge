import { useQuery } from '@tanstack/react-query'
import { getEstimate } from '../jobsService'
import { useWizardStore } from '../../wizardStore'

export function useEstimate() {
  const draft = useWizardStore((s) => s.draft)
  const setEstimate = useWizardStore((s) => s.setEstimate)

  return useQuery({
    queryKey: [
      'estimate',
      draft.documentId,
      draft.template,
      draft.language,
      draft.aiModel,
      draft.coverPage,
      draft.tableOfContents,
      draft.headersFooters,
      draft.placeholderPatterns,
    ],
    queryFn: async () => {
      const est = await getEstimate({
        document_id: draft.documentId!,
        template: draft.template,
        language: draft.language,
        ai_model: draft.aiModel,
        creativity: draft.creativity,
        config: {
          coverPage: draft.coverPage,
          tableOfContents: draft.tableOfContents,
          headersFooters: draft.headersFooters,
          extra_placeholder_patterns: draft.placeholderPatterns,
        },
      })
      setEstimate(est)
      return est
    },
    enabled: draft.documentId != null,
    staleTime: 60_000,
  })
}
