# backend/app/services/chunker.py
import re
from typing import List

_SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\!])\s+')

# Patterns to detect legal markers
_ARTICLE_RE = re.compile(r'\bArticle\s+\d+[A-Za-z0-9\-]*', flags=re.IGNORECASE)
_SECTION_RE = re.compile(r'\bSection\s+\d+[A-Za-z0-9\-]*', flags=re.IGNORECASE)
_BNS_SECTION_RE = re.compile(r'\bBNS\s+Section\s+\d+', flags=re.IGNORECASE)
_ARTICLE_HEADER_RE = re.compile(r'(Article\s+\d+[^\n]*)', flags=re.IGNORECASE)
_SECTION_HEADER_RE = re.compile(r'(Section\s+\d+[^\n]*)', flags=re.IGNORECASE)

def _split_by_marker(text: str, marker_re: re.Pattern) -> List[str]:
    """
    Split text into blocks where each block begins with a marker that matches marker_re.
    Keeps the marker at the beginning of each block.
    """
    parts = []
    last_idx = 0
    for m in marker_re.finditer(text):
        start = m.start()
        if start > last_idx:
            # append previous chunk (if any)
            snippet = text[last_idx:start].strip()
            if snippet:
                parts.append(snippet)
        # find next marker or end
        last_idx = start
    # append the remainder
    remainder = text[last_idx:].strip()
    if remainder:
        parts.append(remainder)
    return parts

def chunk_text_legal_markers(text: str) -> List[str]:
    """
    Try to split by Article/Section/BNS markers.
    Returns a list of chunks if markers are found, else [].
    """
    if _ARTICLE_RE.search(text):
        # attempt to split by article headers
        # split when "Article X" appears - keep header with chunk
        # Use a lookahead to split at every Article occurrence
        article_split = re.split(r'(?=(?:Article\s+\d+[^\n]*))', text, flags=re.IGNORECASE)
        chunks = [a.strip() for a in article_split if a.strip()]
        if len(chunks) > 1:
            return chunks

    # try Section split
    if _SECTION_RE.search(text):
        section_split = re.split(r'(?=(?:Section\s+\d+[^\n]*))', text, flags=re.IGNORECASE)
        chunks = [s.strip() for s in section_split if s.strip()]
        if len(chunks) > 1:
            return chunks

    # try BNS-like pattern
    if _BNS_SECTION_RE.search(text):
        bns_split = re.split(r'(?=(?:BNS\s+Section\s+\d+[^\n]*))', text, flags=re.IGNORECASE)
        chunks = [b.strip() for b in bns_split if b.strip()]
        if len(chunks) > 1:
            return chunks

    return []

def chunk_text(text: str, chunk_size_words: int = 200, overlap_words: int = 50) -> List[str]:
    """
    Smart chunker:
    1. If legal markers (Article/Section/etc.) found -> chunk by marker
    2. Otherwise fallback to sentence-based chunking with word limits and overlap.
    """
    if not text or not text.strip():
        return []

    # first, attempt legal marker chunking
    marker_chunks = chunk_text_legal_markers(text)
    if marker_chunks:
        # Trim whitespace and return
        cleaned = [c.replace('\n', ' ').strip() for c in marker_chunks if c.strip()]
        return cleaned

    # fallback: sentence split then pack into word-limited chunks
    sentences = _SENT_SPLIT_RE.split(text.replace('\r', ' ').replace('\n', ' '))
    chunks: List[str] = []
    current: List[str] = []
    current_word_count = 0

    for s in sentences:
        s = s.strip()
        if not s:
            continue
        words = s.split()
        wcount = len(words)
        if current_word_count + wcount <= chunk_size_words or not current:
            current.append(s)
            current_word_count += wcount
        else:
            chunks.append(" ".join(current).strip())
            # build overlap
            if overlap_words > 0:
                tail_words = " ".join(" ".join(current).split()[-overlap_words:])
                current = [tail_words, s]
                current_word_count = len(tail_words.split()) + wcount
            else:
                current = [s]
                current_word_count = wcount

    if current:
        chunks.append(" ".join(current).strip())

    # final cleanup: remove tiny chunks
    final = [c for c in chunks if len(c.split()) > 10]
    return final
