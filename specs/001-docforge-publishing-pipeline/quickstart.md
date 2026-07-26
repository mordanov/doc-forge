# Quickstart: DocForge Automated Publishing Pipeline

**Date**: 2026-07-26

This quickstart validates a complete installation from scratch to a rendered publication.
Use it after implementation to verify the golden path works end-to-end.

---

## Prerequisites

- Python 3.11+
- `pip` or `uv`
- An OpenAI API key
- (Optional) Unsplash / Pexels API keys for additional image sources

---

## 1. Install

```bash
pip install docforge
# or
uv add docforge
```

Verify:
```bash
docforge version
# Expected: DocForge 1.0.0
```

---

## 2. Create a .env file

```bash
cat > .env << 'EOF'
# Authentication
DOCFORGE_USERNAME=admin
DOCFORGE_PASSWORD=changeme123

# Secret key for JWT signing (min 32 chars)
DOCFORGE_SECRET_KEY=your-very-long-random-secret-key-here

# AI provider
OPENAI_API_KEY=sk-...

# Image providers (optional)
UNSPLASH_ACCESS_KEY=...
PEXELS_API_KEY=...
EOF
```

---

## 3. Initialise

```bash
docforge init
```

Expected output:
```
✓ Environment validated
✓ User account created (admin)
✓ Local project store initialised
✓ Cache directory created
DocForge is ready. Run `docforge doctor` to verify all providers.
```

---

## 4. Verify environment

```bash
docforge doctor
```

Expected output:
```
✓ Python 3.11.x
✓ Dependencies installed
✓ User account provisioned
✓ OpenAI API key valid
✓ Internet connectivity
✓ Cache directory writable
✓ Image libraries (Pillow) available
⚠ Unsplash: API key not configured (optional)
⚠ Pexels: API key not configured (optional)
```

---

## 5. Render a document (CLI)

```bash
docforge render examples/sample-guide.docx output/guide-final.docx \
  --template national_geographic \
  --language en
```

Expected output:
```
Loading document...         ✓ (0.3s)
Analysing structure...      ✓ 8 chapters, 12 placeholders (1.2s)
AI Processing...            ✓ 8 decisions generated (12.4s)
Searching images...         ✓ 47 candidates found (4.1s)
Downloading images...       ✓ 11/12 downloaded, 1 placeholder retained (8.7s)
Rendering...                ✓ (6.3s)
Validation...               ✓ no errors (0.4s)
Export...                   ✓ output/guide-final.docx (0.2s)

Completed in 33.6s
Warnings: 1 (run with --verbose for details)
```

Verify the output file exists and is a valid `.docx`:
```bash
ls -lh output/guide-final.docx
# Expected: file exists, size > 0
```

---

## 6. Analyse a document (CLI)

```bash
docforge analyse examples/sample-guide.docx
```

Expected: structured JSON or human-readable report with chapter list, placeholder inventory, statistics.

---

## 7. Start the HTTP server

```bash
docforge server start
# or
uvicorn docforge.server.app:app --port 8000
```

---

## 8. Authenticate (HTTP API)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:20}..."
```

---

## 9. Upload and render via API

```bash
# Upload
DOC_ID=$(curl -s -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@examples/sample-guide.docx" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['document_id'])")

# Analyse
curl -s -X POST http://localhost:8000/documents/$DOC_ID/analyse \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get estimate
curl -s -X POST http://localhost:8000/jobs/estimate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$DOC_ID\",\"config\":{\"template\":\"minimal\",\"language\":\"en\",\"ai\":{\"provider\":\"openai\",\"model\":\"gpt-4o\",\"creativity\":5},\"images\":{\"enabled\":true,\"policy\":\"auto_search\",\"sources\":[\"wikimedia\"],\"density\":\"balanced\"},\"output\":{\"formats\":[\"docx\"],\"generate_cover\":true,\"generate_toc\":true,\"generate_page_numbers\":true,\"generate_headers_footers\":true},\"validation_level\":\"standard\",\"offline\":false}}" \
  | python3 -m json.tool

# Submit job
JOB_ID=$(curl -s -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$DOC_ID\",\"config\":{\"template\":\"minimal\",\"language\":\"en\",\"ai\":{\"provider\":\"openai\",\"model\":\"gpt-4o\",\"creativity\":5},\"images\":{\"enabled\":true,\"policy\":\"auto_search\",\"sources\":[\"wikimedia\"],\"density\":\"balanced\"},\"output\":{\"formats\":[\"docx\"],\"generate_cover\":true,\"generate_toc\":true,\"generate_page_numbers\":true,\"generate_headers_footers\":true},\"validation_level\":\"standard\",\"offline\":false}}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

# Poll until done
while true; do
  STATUS=$(curl -s http://localhost:8000/jobs/$JOB_ID \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'], d['stage'], d['progress'])")
  echo $STATUS
  if [[ $STATUS == COMPLETED* ]] || [[ $STATUS == FAILED* ]]; then break; fi
  sleep 5
done

# Download result
curl -s http://localhost:8000/jobs/$JOB_ID/download/docx \
  -H "Authorization: Bearer $TOKEN" \
  -o output/api-result.docx

ls -lh output/api-result.docx
```

---

## 10. List projects

```bash
curl -s http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 11. Python API

```python
from docforge import Renderer

renderer = Renderer()
renderer.render(
    input_path="examples/sample-guide.docx",
    output_path="output/guide-python-api.docx"
)
```

Or with builder pattern:
```python
(
    Renderer()
        .template("national_geographic")
        .language("en")
        .provider("openai")
        .model("gpt-4o")
        .creativity(5)
        .render(
            input_path="examples/sample-guide.docx",
            output_path="output/guide-python-api.docx"
        )
)
```

---

## Validation Checklist

After running the quickstart, verify:

- [ ] `docforge version` returns `1.0.0`
- [ ] `docforge init` completes without error
- [ ] `docforge doctor` shows all required checks passing
- [ ] CLI render produces a non-empty `.docx` output file
- [ ] Output DOCX contains: cover page, TOC, headers, footers, Image Sources appendix
- [ ] HTTP server starts and responds to `/system/health`
- [ ] Auth login returns a JWT token
- [ ] Document upload, analysis, and job submission all succeed
- [ ] Job polling reaches `COMPLETED` status
- [ ] Output file downloaded via API matches CLI output quality
- [ ] Project appears in `GET /projects` list
- [ ] Python API produces equivalent output to CLI
