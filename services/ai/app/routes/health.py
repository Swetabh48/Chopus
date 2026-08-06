from fastapi import APIRouter

from app.ollama import check_ollama_health
from app.rag.store import collection_count

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    ollama_ok = await check_ollama_health()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": "up" if ollama_ok else "down",
        "rag_chunks": collection_count(),
    }
