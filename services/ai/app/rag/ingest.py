from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.config import settings
from app.rag.chunking import chunk_text
from app.rag.store import add_chunks

SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts)


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def _collect_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        return [path]

    if path.is_dir():
        files = [
            p
            for p in sorted(path.rglob("*"))
            if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
        ]
        if not files:
            raise ValueError(f"No supported documents found under {path}")
        return files

    raise ValueError(f"Path does not exist: {path}")


async def ingest_path(raw_path: str) -> dict[str, object]:
    path = Path(raw_path).expanduser().resolve()
    files = _collect_files(path)

    ingested: list[dict[str, object]] = []
    total_chunks = 0

    for file_path in files:
        text = _read_file(file_path)
        chunks = chunk_text(
            text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        source = str(file_path)
        count = await add_chunks(
            source=source,
            chunks=chunks,
            metadatas=[
                {"source": source, "chunk_index": index, "filename": file_path.name}
                for index in range(len(chunks))
            ],
        )
        total_chunks += count
        ingested.append({"source": source, "chunks": count})

    return {
        "path": str(path),
        "files": len(ingested),
        "chunks": total_chunks,
        "documents": ingested,
    }
