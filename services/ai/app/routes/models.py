from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ollama import OllamaError, list_ollama_models

router = APIRouter(prefix="/v1", tags=["models"])


@router.get("/models")
async def list_models() -> dict[str, object]:
    try:
        models = await list_ollama_models()
    except OllamaError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    data = []
    for model in models:
        name = model.get("name") or model.get("model")
        if not name:
            continue
        data.append(
            {
                "id": name,
                "object": "model",
                "created": 0,
                "owned_by": "ollama",
            }
        )

    return {"object": "list", "data": data}
