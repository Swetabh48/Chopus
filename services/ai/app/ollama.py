from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from app.config import settings


class OllamaError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_ollama_base_url() -> str:
    return settings.ollama_base_url.rstrip("/")


async def check_ollama_health() -> bool:
    url = f"{get_ollama_base_url()}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.is_success
    except httpx.HTTPError:
        return False


async def list_ollama_models() -> list[dict[str, Any]]:
    url = f"{get_ollama_base_url()}/api/tags"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
        except httpx.HTTPError as error:
            raise OllamaError(f"Failed to reach Ollama: {error}") from error

    if not response.is_success:
        raise OllamaError(
            f"Ollama returned {response.status_code}: {response.text}",
            status_code=response.status_code,
        )

    payload = response.json()
    models = payload.get("models") or []
    return models if isinstance(models, list) else []


async def stream_chat_completions(body: dict[str, Any]) -> AsyncIterator[bytes]:
    """Proxy OpenAI-compatible chat completions to Ollama's /v1 endpoint."""
    url = f"{get_ollama_base_url()}/v1/chat/completions"
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", url, json=body) as response:
                if not response.is_success:
                    error_text = (await response.aread()).decode("utf-8", errors="replace")
                    raise OllamaError(
                        f"Ollama chat failed ({response.status_code}): {error_text}",
                        status_code=response.status_code,
                    )

                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk
        except OllamaError:
            raise
        except httpx.HTTPError as error:
            raise OllamaError(f"Failed to reach Ollama: {error}") from error


async def create_chat_completion(body: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_ollama_base_url()}/v1/chat/completions"
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=body)
        except httpx.HTTPError as error:
            raise OllamaError(f"Failed to reach Ollama: {error}") from error

    if not response.is_success:
        raise OllamaError(
            f"Ollama chat failed ({response.status_code}): {response.text}",
            status_code=response.status_code,
        )

    return response.json()
