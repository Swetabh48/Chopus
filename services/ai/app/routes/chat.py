from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.ollama import OllamaError, create_chat_completion, stream_chat_completions
from app.rag.context import augment_chat_body_with_rag

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat/completions")
async def chat_completions(request: Request) -> Any:
    try:
        body = await request.json()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from error

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    if not body.get("model"):
        raise HTTPException(status_code=400, detail="Field 'model' is required")

    if not isinstance(body.get("messages"), list) or len(body["messages"]) == 0:
        raise HTTPException(status_code=400, detail="Field 'messages' must be a non-empty array")

    try:
        body = await augment_chat_body_with_rag(body)
    except OllamaError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"RAG augmentation failed: {error}") from error

    # Internal-only annotation — never send to Ollama
    rag_sources = body.pop("_rag_sources", None)
    stream = bool(body.get("stream"))

    try:
        if stream:
            return StreamingResponse(
                stream_chat_completions(body),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    **(
                        {"X-Rag-Sources": str(len(rag_sources))}
                        if isinstance(rag_sources, list)
                        else {}
                    ),
                },
            )

        payload = await create_chat_completion(body)
        if isinstance(rag_sources, list):
            payload = {**payload, "rag_sources": rag_sources}
        return JSONResponse(payload)
    except OllamaError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
