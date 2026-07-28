import { useMutation } from '@tanstack/react-query'
import { uploadDocument } from '../documentsService'
import { useWizardStore } from '../../wizardStore'

export function useUploadDocument() {
  const setDocument = useWizardStore((s) => s.setDocument)

  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: (doc) => {
      setDocument(doc, null)
    },
  })
}
