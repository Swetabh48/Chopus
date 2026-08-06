from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import chromadb

from app.config import settings
from app.rag.embeddings import embed_texts
from app.rag.hybrid import hybrid_rerank


@lru_cache(maxsize=1)
def get_collection() -> chromadb.Collection:
    path = Path(settings.chroma_path)
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(path))
    return client.get_or_create_collection(
        name="chopus_docs",
        metadata={"hnsw:space": "cosine"},
    )


async def add_chunks(
    *,
    source: str,
    chunks: list[str],
    metadatas: list[dict[str, Any]] | None = None,
) -> int:
    if not chunks:
        return 0

    # Replace previous chunks for this source so re-ingest stays fresh.
    delete_source(source)

    collection = get_collection()
    embeddings = await embed_texts(chunks)
    ids = [f"{source}:{uuid4().hex}" for _ in chunks]
    meta = metadatas or [{"source": source, "chunk_index": i} for i in range(len(chunks))]

    for item in meta:
        item.setdefault("source", source)

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=meta,
    )
    return len(chunks)


async def query_chunks(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []

    final_k = top_k or settings.rag_top_k
    fetch_k = min(max(settings.rag_fetch_k, final_k), total)
    query_embedding = (await embed_texts([query]))[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    candidates: list[dict[str, Any]] = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        # Chroma cosine space: distance ≈ 1 - cosine_similarity
        similarity = max(0.0, 1.0 - float(distance))
        if similarity < settings.rag_min_similarity:
            continue
        candidates.append(
            {
                "text": doc,
                "source": (meta or {}).get("source", "unknown"),
                "filename": (meta or {}).get("filename"),
                "chunk_index": (meta or {}).get("chunk_index"),
                "distance": float(distance),
                "similarity": similarity,
            }
        )

    if not candidates:
        return []

    if settings.rag_hybrid and len(candidates) > 1:
        texts = [str(item["text"]) for item in candidates]
        sims = [float(item["similarity"]) for item in candidates]
        order = hybrid_rerank(
            query=query,
            texts=texts,
            vector_similarities=sims,
            vector_weight=settings.rag_vector_weight,
            top_k=final_k,
        )
        return [candidates[i] for i in order]

    candidates.sort(key=lambda item: item["similarity"], reverse=True)
    return candidates[:final_k]


def list_sources() -> list[dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    data = collection.get(include=["metadatas"])
    metadatas = data.get("metadatas") or []
    counts: dict[str, int] = {}
    for meta in metadatas:
        source = (meta or {}).get("source", "unknown")
        counts[source] = counts.get(source, 0) + 1

    return [
        {"source": source, "chunks": chunk_count}
        for source, chunk_count in sorted(counts.items())
    ]


def delete_source(source: str) -> int:
    collection = get_collection()
    existing = collection.get(where={"source": source})
    ids = existing.get("ids") or []
    if not ids:
        return 0
    collection.delete(ids=ids)
    return len(ids)


def clear_all() -> int:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return 0

    data = collection.get()
    ids = data.get("ids") or []
    if ids:
        collection.delete(ids=ids)
    return count


def collection_count() -> int:
    return get_collection().count()
