#!/usr/bin/env python3
"""
Document Intake — convert PDF/DOCX to clean markdown.

Uses Marker (full OCR layout) when surya models are available.
Falls back to PyMuPDF (text-only) when models can't be downloaded.

Usage:
    python scripts/doc_intake.py <file> [--output <dir>]
    python scripts/doc_intake.py <file> --format text
"""

import sys
import os
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent


def convert_with_marker(pdf_path: str) -> str:
    """Convert PDF using Marker (full OCR + layout)."""
    try:
        from marker_single import marker_single
        # This would need the CLI approach
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "marker_single", pdf_path,
             "--output_format", "markdown", "--output_dir", "/tmp/marker_out"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # Find output file
            out_dir = Path("/tmp/marker_out")
            for f in out_dir.glob("*.md"):
                return f.read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def convert_with_pymupdf(pdf_path: str) -> str:
    """Convert PDF using PyMuPDF (text extraction, no OCR)."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text_parts = []
        for i, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"<!-- Page {i+1} -->\n{page_text}")
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error: {e}"


def convert_pdf(pdf_path: str) -> str:
    """Convert PDF to markdown. Try Marker first, fallback to PyMuPDF."""
    # Try Marker
    md = convert_with_marker(pdf_path)
    if md and len(md) > 50:
        return md

    # Fallback to PyMuPDF
    return convert_with_pymupdf(pdf_path)


def convert_docx(docx_path: str) -> str:
    """Convert DOCX to markdown."""
    try:
        from docx import Document
        doc = Document(docx_path)
        parts = []
        for para in doc.paragraphs:
            if para.style.name.startswith("Heading"):
                level = para.style.name.replace("Heading ", "")
                parts.append(f"{'#' * int(level)} {para.text}")
            elif para.text.strip():
                parts.append(para.text)
        return "\n\n".join(parts)
    except Exception as e:
        return f"Error: {e}"


def convert_file(file_path: str) -> str:
    """Convert any supported file to markdown."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"

    ext = path.suffix.lower()
    if ext == ".pdf":
        return convert_pdf(str(path))
    elif ext in (".docx", ".doc"):
        return convert_docx(str(path))
    elif ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        return f"Error: Unsupported format: {ext}"


# CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doc_intake.py <file> [--output <dir>]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    result = convert_file(file_path)

    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        out_file = out / (Path(file_path).stem + ".md")
        out_file.write_text(result, encoding="utf-8")
        print(f"Saved to: {out_file}")
        print(f"Size: {len(result)} chars")
    else:
        print(result)
