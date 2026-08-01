---
name: document-intake
description: Convert PDF/DOCX to clean markdown for agent processing
category: productivity
tags: [pdf, docx, markdown, document, ocr]
---

# Document Intake

Convert PDF and DOCX files to clean markdown for agent processing.

## Trigger

User asks to convert a document, extract text from PDF, or process a file.

## Steps

1. Run: `python scripts/doc_intake.py <file> [--output <dir>]`
2. Script tries Marker (full OCR) first, falls back to PyMuPDF (text-only)
3. Output: clean markdown with page markers

## Supported Formats

- **PDF** → Marker (OCR + layout) or PyMuPDF (text extraction)
- **DOCX** → python-docx (paragraphs + headings)
- **TXT** → direct read

## Examples

```bash
# Convert PDF to stdout
python scripts/doc_intake.py document.pdf

# Convert PDF to file
python scripts/doc_intake.py document.pdf --output cache/

# Convert DOCX
python scripts/doc_intake.py report.docx --output cache/
```

## Pitfalls

- Marker needs surya models (~2GB download). If SSL blocks download, PyMuPDF fallback is used (text only, no OCR)
- PyMuPDF can't extract text from scanned images (use Marker for those)
- Large PDFs (>100 pages) may be slow with Marker

## Dependencies

- `marker-pdf` (installed)
- `PyMuPDF` (installed with marker-pdf)
- `python-docx` (for DOCX support)
