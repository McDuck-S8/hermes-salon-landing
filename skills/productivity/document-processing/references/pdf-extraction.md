# PDF Extraction — Full Reference

## pymupdf (lightweight)

### Installation

```bash
pip install pymupdf pymupdf4llm
```

### Via Helper Script

Available in `scripts/extract_pymupdf.py`:

```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

### Inline

```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

## marker-pdf (high-quality OCR)

### Prerequisites

Check disk space first — needs ~5GB for PyTorch + models:
```bash
python scripts/extract_marker.py --check
```

### Installation

```bash
pip install marker-pdf
```

### Via Helper Script

```bash
python scripts/extract_marker.py document.pdf                        # Markdown
python scripts/extract_marker.py document.pdf --json                 # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/      # Save images
python scripts/extract_marker.py scanned.pdf                         # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm              # LLM-boosted accuracy
```

### CLI (installed with marker-pdf)

```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4      # Batch
```

## Split, Merge & Search

pymupdf handles these natively:

### Split: extract pages 1-5 to a new PDF

```python
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

### Merge multiple PDFs

```python
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

### Search for text across all pages

```python
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

## Notes

- `web_extract` is always first choice for URLs (no local deps)
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx`
- For PowerPoint: see the `powerpoint` skill
