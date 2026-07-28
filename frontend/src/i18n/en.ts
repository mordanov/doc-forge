const en = {
  // App / nav
  appName: 'DocForge',
  nav: {
    home: 'Home',
    newProject: 'New Project',
    projects: 'Projects',
    settings: 'Settings',
    about: 'About',
  },

  // Auth
  login: {
    subtitle: 'Sign in to your account',
    username: 'Username',
    password: 'Password',
    submit: 'Sign in',
    submitting: 'Signing in…',
    error: 'Login failed. Check your credentials.',
    usernameRequired: 'Username is required',
    passwordRequired: 'Password is required',
  },

  // Home
  home: {
    tagline: 'Transform your Word documents into beautifully formatted publications.',
    recentProjects: 'Recent Projects',
    newBtn: 'New',
    browseAll: 'Browse all',
    noProjects: 'No projects yet. Drop a file above to get started.',
    uploading: 'Uploading…',
  },

  // Projects
  projects: {
    title: 'Projects',
    newProject: 'New Project',
    createPublication: 'Create Publication',
    noProjects: 'No projects yet',
    previous: 'Previous',
    next: 'Next',
    download: 'Download',
    duplicate: 'Duplicate',
    open: 'Open',
    delete: 'Delete',
    deleteTitle: 'Delete project?',
    deleteDescription: (name: string) =>
      `"${name}" will be permanently deleted and cannot be recovered.`,
    cancel: 'Cancel',
  },

  // Settings
  settings: {
    title: 'Settings',
    appearance: 'Appearance',
    darkMode: 'Dark Mode',
    darkModeDesc: 'Switch between light and dark interface',
    defaults: 'Defaults',
    defaultLanguage: 'Default Language',
    defaultFormat: 'Default Output Format',
    defaultTemplate: 'Default Template',
    apiKeys: 'API Keys',
    openAiKey: 'OpenAI API Key',
    openAiKeyHint: 'Stored locally. Never logged or transmitted to third parties.',
    save: 'Save Settings',
    saving: 'Saving…',
    saved: 'Saved',
  },

  // About
  about: {
    title: 'About DocForge',
    whatTitle: 'What is DocForge?',
    whatBody:
      'DocForge transforms Word documents into beautifully formatted publications using AI. Upload a .docx file, configure AI and publication settings, and download a polished output.',
    linksTitle: 'Links',
    github: 'GitHub Repository',
    docs: 'Documentation',
    contributorsTitle: 'Contributors',
    contributorsBody:
      'DocForge is an open-source project. See the GitHub repository for a full list of contributors.',
    licenceTitle: 'Licence',
    licenceBody: 'DocForge is released under the',
    licenceName: 'MIT Licence',
    licenceTrail: '. You are free to use, modify, and distribute this software in accordance with its terms.',
  },

  // Wizard nav
  wizardNav: {
    steps: {
      1: 'Upload',
      2: 'AI Config',
      3: 'Publication',
      4: 'Preview',
      5: 'Generate',
    },
    back: 'Back',
    next: 'Next',
    loading: 'Loading…',
  },

  // Wizard — resume dialog
  wizardResume: {
    title: 'Resume your project?',
    description: (filename: string) =>
      `You have an unfinished project — ${filename}. Would you like to continue where you left off?`,
    startFresh: 'Start fresh',
    continue: 'Continue',
  },

  // Step 1
  step1: {
    title: 'Upload Document',
    subtitle: 'Select a .docx file to begin',
    uploading: 'Uploading…',
    analysing: 'Analysing document…',
    uploadFailed: 'Upload failed. Please try again.',
    remove: 'Remove',
    stats: {
      pages: 'Pages',
      headings: 'Headings',
      tables: 'Tables',
      images: 'Images',
      words: 'Words',
      chapters: 'Chapters',
    },
  },

  // Step 2
  step2: {
    title: 'AI Configuration',
    subtitle: 'Choose how the AI processes your document',
    provider: 'AI Provider',
    providerOnly: 'Only OpenAI is supported in this version',
    model: 'Model',
    quality: 'Quality',
    creativity: 'Creativity',
    creativityDescriptions: {
      1: 'Strictly factual — no creative rewriting',
      2: 'Minimal creative input',
      3: 'Light editorial touch',
      4: 'Some rewriting for clarity',
      5: 'Balanced — moderate creative input',
      6: 'Enhanced readability and flow',
      7: 'Notable creative rewriting',
      8: 'Strong editorial voice',
      9: 'High creativity — significant rewrites',
      10: 'Maximum creativity — fully reimagined prose',
    },
    qualityOptions: {
      fast: 'Fast',
      balanced: 'Balanced',
      maximum: 'Maximum Quality',
    },
    qualityDescs: {
      fast: 'Quicker results, lower cost',
      balanced: 'Good quality, reasonable speed',
      maximum: 'Best results, takes longer',
    },
  },

  // Step 3
  step3: {
    title: 'Publication Configuration',
    subtitle: 'Choose a preset or configure settings individually',
    preset: 'Preset',
    theme: 'Theme',
    language: 'Language',
    outputFormats: 'Output Formats',
    typography: 'Typography',
    sidebarStyle: 'Sidebar Style',
    coverPage: 'Cover Page',
    tableOfContents: 'Table of Contents',
    headersFooters: 'Headers & Footers',
    imageDensity: 'Image Density',
    layoutDensity: 'Layout Density',
    colourPalette: 'Colour Palette',
    validationLevel: 'Validation Level',
    imagePolicy: 'Image Policy',
    imageSources: 'Image Sources',
    imageSourcesDesc: 'Pexels and Unsplash require API keys set in Settings.',
    offlineMode: 'Offline Mode',
    offlineModeDesc: 'Use only cached resources',
    advancedSettings: 'Advanced Settings',
    parallelDownloads: 'Parallel Downloads',
    retryCount: 'Retry Count',
    timeout: 'Timeout (s)',
    hints: {
      preset: 'A preset combines all settings below into a ready-made configuration for a specific document type.',
      theme: 'The visual template that controls fonts, colours, and page layout of the output document.',
      language: 'The language used for generated captions, section headings, and table of contents.',
      outputFormats: 'Choose one or more file formats for the final document. DOCX is always available.',
      typography: 'Controls body text style. Conservative is classic serif; Editorial adds line-height; Magazine uses Calibri; Luxury uses larger body text.',
      sidebarStyle: 'Adds a side panel to chapters. None disables it; Minimal shows a plain snippet; Editorial and Magazine add styled side notes.',
      coverPage: 'Whether to include a cover page. Simple shows the title; Full adds author and date.',
      tableOfContents: 'Include a table of contents. Standard lists chapter titles; Detailed shows sub-headings too.',
      headersFooters: 'Page header and footer content. Standard shows document title in header and page number in footer.',
      imageDensity: 'Controls how many images are inserted. Minimal adds very few; Maximum fills every available placeholder.',
      layoutDensity: 'Controls whitespace and margins. Compact is tighter; Spacious adds breathing room between sections.',
      colourPalette: 'The colour scheme applied to headings, dividers, and highlights throughout the document.',
      validationLevel: 'Fast skips optional checks. Strict enforces all structural and formatting rules.',
      imagePolicy: 'Auto searches and inserts images. Placeholders Only keeps text markers. Preserve keeps images from the original file. Disable removes all images.',
      imageSources: 'Which image providers to search. Wikimedia is free; Pexels and Unsplash require API keys.',
      offlineMode: 'When enabled, only resources already cached locally are used — no network requests for images or fonts.',
      parallelDownloads: 'Number of image downloads that run simultaneously. Higher values speed up large documents.',
      retryCount: 'How many times a failed download or AI call is retried before being skipped.',
      timeout: 'Maximum seconds to wait for a single network request before it is considered failed.',
    },
  },

  // Step 4
  step4: {
    title: 'Preview',
    subtitle: 'Review the estimate before generating',
    warnings: (n: number) => `Warnings (${n})`,
    validationPassed: 'Validation passed — no errors found',
    licenceSummary: 'Licence Summary',
    licensed: (n: number, providers: string) => `${n} licensed image(s) from ${providers}`,
    unlicensed: (n: number) => `, ${n} may require attribution`,
    generateFailed: 'Failed to start job. Please try again.',
    generate: 'Generate',
    estimatedCost: 'Est. cost',
  },

  // Step 5
  step5: {
    title: 'Generating',
    connectionLost: 'Connection lost — retrying…',
    download: 'Download',
    viewProjects: 'View Projects',
    failed: 'Generation failed',
    cancelled: 'Job was cancelled.',
    backToSettings: 'Back to settings',
    stages: {
      UPLOADING: 'Uploading',
      LOADING: 'Loading',
      ANALYSING: 'Analysing',
      AI_PROCESSING: 'AI Processing',
      SEARCHING_IMAGES: 'Searching Images',
      DOWNLOADING_IMAGES: 'Downloading Images',
      RENDERING: 'Rendering',
      VALIDATION: 'Validation',
      EXPORT: 'Export',
      FINISHED: 'Finished',
    },
  },

  // Upload area
  uploadArea: {
    cta: 'Click or drop a .docx file here',
    invalidType: 'Only .docx files are accepted',
    tooLarge: (limit: string) => `File exceeds the ${limit} limit`,
  },
}

export type Translations = typeof en
export default en
