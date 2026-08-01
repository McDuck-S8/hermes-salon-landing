# Document Intake — Marker + PyMuPDF Reference

## Marker-pdf Status (2026-07-09)

**Installed**: marker-pdf 1.10.2
**CLI**: `marker_single <file> --output_format markdown --output_dir <dir>`

### Problem: surya模型下载失败
Marker needs OCR models from `models.datalab.to`. On Windows with SSL issues:
```
SSLError: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol
```

### Solution: PyMuPDF Fallback
`fitz` (PyMuPDF) is installed with marker-pdf. Text-only extraction, no OCR:

```python
import fitz
doc = fitz.open(pdf_path)
text = "\n".join(page.get_text() for page in doc)
doc.close()
```

### doc_intake.py Implementation
```python
def convert_pdf(pdf_path: str) -> str:
    """Try Marker first, fallback to PyMuPDF."""
    md = convert_with_marker(pdf_path)  # Full OCR + layout
    if md and len(md) > 50:
        return md
    return convert_with_pymupdf(pdf_path)  # Text-only fallback
```

### Marker API Changes (v1.10+)
- `result.markdown_v2` → DEPRECATED. Use `result.markdown` (returns `MarkdownGenerationResult`)
- `MarkdownGenerationResult.raw_markdown` — clean markdown string
- `MarkdownGenerationResult.fit_markdown` — filtered/optimized text

### When to Use Which
| Scenario | Tool | Notes |
|----------|------|-------|
| Text PDF | PyMuPDF | Fast, no models needed |
| Scanned PDF | Marker | Needs surya models (fix SSL first) |
| DOCX | python-docx | Paragraphs + headings |
| Large PDF (>100p) | Marker | Slow but accurate |
