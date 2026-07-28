import { describe, it, expect, beforeEach } from 'vitest'
import { useWizardStore } from '@/features/wizard/wizardStore'

beforeEach(() => {
  sessionStorage.clear()
  useWizardStore.setState({
    draft: {
      step: 1,
      documentId: null,
      filename: null,
      analysis: null,
      aiProvider: 'openai',
      aiModel: 'gpt-4o',
      aiQuality: 'balanced',
      creativity: 5,
      presetId: null,
      template: 'minimal',
      outputFormats: ['docx'],
      language: 'en',
      imagePolicy: 'auto',
      imageSources: ['pexels'],
      imageDensity: 'balanced',
      layoutDensity: 'balanced',
      typography: 'serif',
      colourPalette: 'auto',
      customColour: null,
      sidebarStyle: 'none',
      coverPage: 'simple',
      tableOfContents: 'standard',
      headersFooters: 'standard',
      validationLevel: 'standard',
      aiExplainability: 'off',
      offlineMode: false,
      promptVersion: null,
      themeVersion: null,
      parallelDownloads: 3,
      retryCount: 3,
      timeout: 300,
      cacheLocation: null,
      cacheSize: null,
      maxAiRequests: null,
      estimate: null,
      activeJobId: null,
    },
    hasSavedDraft: false,
  })
})

describe('wizardStore', () => {
  it('starts at step 1', () => {
    expect(useWizardStore.getState().draft.step).toBe(1)
  })

  it('goNext advances step', () => {
    useWizardStore.getState().goNext()
    expect(useWizardStore.getState().draft.step).toBe(2)
  })

  it('goBack decrements step', () => {
    useWizardStore.getState().goNext()
    useWizardStore.getState().goBack()
    expect(useWizardStore.getState().draft.step).toBe(1)
  })

  it('does not go below step 1', () => {
    useWizardStore.getState().goBack()
    expect(useWizardStore.getState().draft.step).toBe(1)
  })

  it('does not go above step 5', () => {
    for (let i = 0; i < 10; i++) useWizardStore.getState().goNext()
    expect(useWizardStore.getState().draft.step).toBe(5)
  })

  it('applyPreset updates template', () => {
    useWizardStore.getState().applyPreset('travel-guide')
    expect(useWizardStore.getState().draft.presetId).toBe('travel-guide')
    expect(useWizardStore.getState().draft.template).toBe('lonely_planet')
  })

  it('reset returns to step 1 with no document', () => {
    useWizardStore.getState().setDocument({ id: 'd1', filename: 'test.docx', size: 100 }, null)
    useWizardStore.getState().goNext()
    useWizardStore.getState().reset()
    expect(useWizardStore.getState().draft.step).toBe(1)
    expect(useWizardStore.getState().draft.documentId).toBeNull()
  })
})
