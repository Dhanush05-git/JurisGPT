# backend/app/services/document_loader.py
import os
import json
import csv

def load_document(path: str) -> str:
    """
    Load textual content from a file path.
    Supports: .txt, .json, .csv
    Optional: .pdf (PyPDF2), .docx (python-docx) if packages installed.
    Returns the extracted text (string).
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, str):
                return data
            elif isinstance(data, dict):
                # join values
                return " ".join([str(v) for v in data.values()])
            elif isinstance(data, list):
                return " ".join([str(x) for x in data])
            else:
                return str(data)

    if ext == ".csv":
        parts = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                parts.append(" ".join(row))
        return "\n".join(parts)

    if ext == ".pdf":
        # optional dependency: PyPDF2
        try:
            import PyPDF2
        except Exception:
            raise RuntimeError("PyPDF2 not installed. Install it to load PDFs (pip install PyPDF2).")
        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                try:
                    text_parts.append(page.extract_text() or "")
                except Exception:
                    continue
        return "\n".join(text_parts)

    if ext in [".docx", ".doc"]:
        try:
            import docx
        except Exception:
            raise RuntimeError("python-docx not installed. Install it to load docx files (pip install python-docx).")
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs)

    # fallback: try reading as text
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        raise RuntimeError(f"Unsupported file type or cannot read file: {path}")
