---
name: document-processing
description: "Extract text from PDFs/scans (pymupdf, marker-pdf) and edit PDF content via natural language (nano-pdf). Also covers split, merge, search, and OCR workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pdf, documents, ocr, text-extraction, editing, markdown, scanning]
    related_skills: [powerpoint]
---

# Document Processing

Extract, edit, and manipulate PDF documents and scanned files. Two complementary sub-workflows:

- **PDF & Document Extraction** — extract text from PDFs/scans using pymupdf (lightweight) or marker-pdf (full OCR + complex layouts)
- **PDF Editing** — edit PDF text/typos/titles via natural-language prompts using nano-pdf

---

## 1. PDF & Document Extraction

For DOCX: use `python-docx`. For PPTX: see the `powerpoint` skill.
This covers **PDFs and scanned documents**.

### Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.
Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

### Step 2: Choose Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| Text-based PDF | ✅ | ✅ |
| Scanned PDF (OCR) | ❌ | ✅ (90+ languages) |
| Tables | ✅ (basic) | ✅ (high accuracy) |
| Equations / LaTeX | ❌ | ✅ |
| Markdown output | ✅ (via pymupdf4llm) | ✅ (native) |
| Install size | ~25MB | ~3-5GB (PyTorch + models) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

**Pitfall — marker-pdf model download fails with SSL on Windows:**
Marker needs surya models from `models.datalab.to`. This fails with `SSLEOFError` on this system.
**Fix:** pymupdf is the automatic fallback (doc_intake.py handles this). For marker-pdf specifically, models must be pre-cached or downloaded via a proxy/machine with working SSL.

**Pitfall — Crawl4AI needs Playwright browsers (SSL download fails on Windows):**
Crawl4AI uses Playwright for headless browsing. `playwright install chromium` fails with SSL errors on this system.
**Fix:** If existing Playwright browsers are installed (check `C:\Users\Asus\AppData\Local\ms-playwright\`), create a symlink:
```bash
cmd.exe /c "mklink /D \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1228\" \"C:\Users\Asus\AppData\Local\ms-playwright\chromium_headless_shell-1223\""
```
Adjust version numbers to match what's installed vs what Crawl4AI expects. Check error message for the required version.

### pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

Helper scripts are available at `scripts/extract_pymupdf.py` and `scripts/extract_marker.py` (under this skill directory). Run them from the skill directory or copy them to your project.

**Inline extraction:**
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

Use the helper scripts in `scripts/` if available (check with ls). See `references/pdf-extraction.md` for full pymupdf and marker-pdf workflows including Arxiv papers, split/merge/search.

### Unified doc_intake.py (OKF-Lite compatible)

```bash
python scripts/doc_intake.py document.pdf                    # stdout
python scripts/doc_intake.py document.pdf --output cache/    # save to file
python scripts/doc_intake.py report.docx --output cache/     # DOCX too
```
Tries Marker first (full OCR), falls back to PyMuPDF (text-only). Supports PDF, DOCX, TXT.

### Arxiv Papers

```
web_extract(urls=["https://arxiv.org/abs/2402.03300"])
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_search(query="arxiv GRPO reinforcement learning 2026")
```

---

## 2. PDF Editing (nano-pdf)

Edit PDFs using natural-language instructions. Point it at a page and describe what to change.

### Prerequisites

```bash
uv pip install nano-pdf
# or
pip install nano-pdf
```

### Usage

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

### Examples

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"

# Update a date on a specific page
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

### Notes

- Page numbers may be 0-based or 1-based depending on version
- Always verify the output PDF after editing
- The tool uses an LLM under the hood — requires an API key
- Works well for text changes; complex layout modifications may need a different approach

---

## Related Skills

- `powerpoint` — PPTX creation and editing (python-pptx)
