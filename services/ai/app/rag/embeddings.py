from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.ollama import OllamaError, get_ollama_base_url


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    base = get_ollama_base_url()
    vectors: list[list[float]] = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Prefer modern /api/embed (supports batch); fall back to legacy /api/embeddings.
        try:
            response = await client.post(
                f"{base}/api/embed",
                json={"model": settings.embedding_model, "input": texts},
            )
            if response.is_success:
                payload: dict[str, Any] = response.json()
                embeddings = payload.get("embeddings")
                if isinstance(embeddings, list) and len(embeddings) == len(texts):
                    return embeddings
        except httpx.HTTPError:
            pass

        for text in texts:
            try:
                response = await client.post(
                    f"{base}/api/embeddings",
                    json={"model": settings.embedding_model, "prompt": text},
                )
            except httpx.HTTPError as error:
                raise OllamaError(f"Failed to reach Ollama embeddings: {error}") from error

            if not response.is_success:
                raise OllamaError(
                    f"Ollama embeddings failed ({response.status_code}): {response.text}. "
                    f"Pull the embedding model with: ollama pull {settings.embedding_model}",
                    status_code=response.status_code,
                )

            payload = response.json()
            embedding = payload.get("embedding")
            if not isinstance(embedding, list) or not embedding:
                raise OllamaError("Ollama returned an empty embedding")
            vectors.append(embedding)

    return vectors
