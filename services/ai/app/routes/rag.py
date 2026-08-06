from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.ingest import ingest_path
from app.rag.store import clear_all, collection_count, delete_source, list_sources, query_chunks

router = APIRouter(prefix="/v1/rag", tags=["rag"])


class IngestRequest(BaseModel):
    path: str = Field(..., description="Absolute or relative path to a file or folder")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


@router.get("/status")
async def rag_status() -> dict[str, object]:
    return {
        "chunks": collection_count(),
        "sources": list_sources(),
    }


@router.get("/documents")
async def rag_documents() -> dict[str, object]:
    return {"documents": list_sources()}


@router.post("/query")
async def rag_query(body: QueryRequest) -> dict[str, object]:
    hits = await query_chunks(body.query, top_k=body.top_k)
    return {"query": body.query, "hits": hits}


@router.post("/ingest")
async def rag_ingest(body: IngestRequest) -> dict[str, object]:
    try:
        result = await ingest_path(body.path)
        return result
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/documents")
async def rag_clear() -> dict[str, object]:
    deleted = clear_all()
    return {"deleted_chunks": deleted}


@router.delete("/documents/{source:path}")
async def rag_delete_source(source: str) -> dict[str, object]:
    deleted = delete_source(source)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No chunks for source: {source}")
    return {"source": source, "deleted_chunks": deleted}
