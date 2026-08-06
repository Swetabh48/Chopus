from __future__ import annotations

import re


_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n+")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Paragraph-aware chunking with sentence fallback (better than fixed char cuts)."""
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    paragraphs = [part.strip() for part in _PARAGRAPH_SPLIT.split(cleaned) if part.strip()]
    if not paragraphs:
        paragraphs = [cleaned]

    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            units.append(paragraph)
            continue
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(paragraph) if s.strip()]
        if len(sentences) <= 1:
            units.extend(_hard_slice(paragraph, chunk_size, overlap))
            continue
        units.extend(_pack_units(sentences, chunk_size))

    return _pack_units(units, chunk_size) if any(len(u) > chunk_size for u in units) else units


def _pack_units(parts: list[str], chunk_size: int) -> list[str]:
    chunks: list[str] = []
    buf = ""
    for part in parts:
        if not part:
            continue
        if len(part) > chunk_size:
            if buf:
                chunks.append(buf)
                buf = ""
            chunks.extend(_hard_slice(part, chunk_size, max(40, chunk_size // 6)))
            continue
        candidate = f"{buf}\n\n{part}".strip() if buf else part
        if len(candidate) <= chunk_size:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            buf = part
    if buf:
        chunks.append(buf)
    return chunks


def _hard_slice(text: str, chunk_size: int, overlap: int) -> list[str]:
    collapsed = " ".join(text.split())
    if len(collapsed) <= chunk_size:
        return [collapsed] if collapsed else []

    chunks: list[str] = []
    start = 0
    while start < len(collapsed):
        end = min(len(collapsed), start + chunk_size)
        chunks.append(collapsed[start:end])
        if end >= len(collapsed):
            break
        start = max(0, end - overlap)
    return chunks
