# backend/app/services/document_loader.py
import os
from typing import List
import pdfplumber
import docx
import pandas as pd
import json

def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                texts.append(txt)
    return "\n".join(texts)

def read_docx(path: str) -> str:
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)

def read_csv(path: str) -> str:
    # Read CSV and concatenate text-like columns
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception:
        # try with python engine fallback
        df = pd.read_csv(path, dtype=str, engine="python", keep_default_na=False)
    # join all cell values into lines
    rows = []
    for _, row in df.iterrows():
        vals = [str(v).strip() for v in row.values if str(v).strip()]
        if vals:
            rows.append(" | ".join(vals))
    return "\n".join(rows)

def read_json(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # recursively extract strings
    texts = []

    def _extract(obj):
        if obj is None:
            return
        if isinstance(obj, dict):
            for v in obj.values():
                _extract(v)
        elif isinstance(obj, list):
            for v in obj:
                _extract(v)
        elif isinstance(obj, (str, int, float, bool)):
            texts.append(str(obj))
        else:
            try:
                texts.append(str(obj))
            except Exception:
                pass

    _extract(data)
    return "\n".join(texts)

def load_document(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt"]:
        return read_txt(path)
    if ext in [".pdf"]:
        return read_pdf(path)
    if ext in [".docx", ".doc"]:
        return read_docx(path)
    if ext in [".csv"]:
        return read_csv(path)
    if ext in [".json"]:
        return read_json(path)
    # fallback: try txt
    return read_txt(path)
