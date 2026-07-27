import { http, HttpResponse } from 'msw'

const MOCK_TOKEN = 'mock-jwt-token'

export const handlers = [
  http.post('/auth/login', () =>
    HttpResponse.json({ access_token: MOCK_TOKEN, token_type: 'bearer' })
  ),

  http.get('/system/health', () =>
    HttpResponse.json({ status: 'ok', version: '0.1.0' })
  ),

  http.get('/system/themes', () =>
    HttpResponse.json([
      { id: 'minimal', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: false },
      { id: 'dk_eyewitness', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: true },
      { id: 'lonely_planet', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: true },
      { id: 'national_geographic', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: false },
      { id: 'corporate', version: '1.0', author: 'DocForge', supports_cover: true, supports_sidebars: true },
    ])
  ),

  http.get('/system/providers', () =>
    HttpResponse.json({
      ai: [{ id: 'openai', available: true }],
      images: [
        { id: 'pexels', available: true, requires_key: true },
        { id: 'unsplash', available: true, requires_key: true },
      ],
    })
  ),

  http.post('/documents/upload', () =>
    HttpResponse.json({ id: 'doc-mock-001', filename: 'document.docx', size: 102400 })
  ),

  http.post('/documents/:docId/analyse', () =>
    HttpResponse.json({
      document_id: 'doc-mock-001',
      statistics: {
        chapters: 3,
        headings: 12,
        tables: 2,
        image_placeholders: 5,
        words: 4200,
        estimated_pages: 18,
      },
      issues: [],
    })
  ),

  http.post('/jobs/estimate', () =>
    HttpResponse.json({
      estimated_rendering_seconds: 45,
      estimated_ai_tokens: 12000,
      estimated_ai_requests: 8,
      estimated_page_count: 18,
      image_placeholder_count: 5,
      validation_summary: { warnings: [], errors: [] },
      licence_summary: { providers_available: ['pexels'], expected_licensed: 4, expected_unlicensed: 1 },
    })
  ),

  http.post('/jobs', () =>
    HttpResponse.json({ job_id: 'job-mock-001', status: 'QUEUED' })
  ),

  http.get('/jobs/:jobId', ({ params }) => {
    const { jobId } = params
    return HttpResponse.json({
      id: jobId,
      project_id: 'proj-mock-001',
      status: 'COMPLETED',
      stage: 'FINISHED',
      progress: 100,
      elapsed_seconds: 42,
      config_snapshot: '{}',
      input_filename: 'document.docx',
      input_path: '/tmp/document.docx',
      output_paths: '["output/document.docx"]',
      warnings: '[]',
      error: null,
      created_at: new Date().toISOString(),
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    })
  }),

  http.get('/jobs/:jobId/download', () =>
    new HttpResponse(new Blob(['mock content'], { type: 'application/octet-stream' }), {
      headers: { 'Content-Disposition': 'attachment; filename="output.docx"' },
    })
  ),

  http.get('/projects', () =>
    HttpResponse.json([
      {
        id: 'proj-mock-001',
        name: 'Travel Guide 2026',
        job_id: 'job-mock-001',
        input_filename: 'document.docx',
        config_snapshot: '{}',
        output_paths: '["output/document.docx"]',
        template: 'lonely_planet',
        language: 'en',
        ai_model: 'gpt-4o',
        status: 'COMPLETED',
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      },
    ])
  ),

  http.get('/projects/:id', ({ params }) =>
    HttpResponse.json({
      id: params.id,
      name: 'Travel Guide 2026',
      job_id: 'job-mock-001',
      input_filename: 'document.docx',
      config_snapshot: '{}',
      output_paths: '["output/document.docx"]',
      template: 'lonely_planet',
      language: 'en',
      ai_model: 'gpt-4o',
      status: 'COMPLETED',
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    })
  ),

  http.post('/projects/:id/duplicate', () =>
    HttpResponse.json({ job_id: 'job-mock-002', status: 'QUEUED' })
  ),

  http.delete('/projects/:id', () =>
    new HttpResponse(null, { status: 204 })
  ),
]
