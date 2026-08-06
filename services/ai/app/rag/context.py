from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.rag.store import collection_count, query_chunks


def _extract_last_user_text(messages: list[dict[str, Any]]) -> str | None:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text")
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(part, str):
                    parts.append(part)
            joined = "\n".join(parts).strip()
            if joined:
                return joined
    return None


def _short_source(source: str) -> str:
    try:
        return Path(source).name
    except Exception:
        return source


def format_context(hits: list[dict[str, Any]], max_chars: int) -> str:
    blocks: list[str] = []
    used = 0
    for index, hit in enumerate(hits, start=1):
        source = _short_source(str(hit.get("source", "unknown")))
        text = str(hit.get("text", "")).strip()
        similarity = hit.get("similarity")
        header = f"[{index}] {source}"
        if isinstance(similarity, (int, float)):
            header += f" (relevance {similarity:.2f})"
        block = f"{header}\n{text}"
        extra = len(block) + (2 if blocks else 0)
        if used + extra > max_chars:
            remaining = max_chars - used - len(header) - 5
            if remaining > 80:
                blocks.append(f"{header}\n{text[:remaining]}…")
            break
        blocks.append(block)
        used += extra
    return "\n\n".join(blocks)


async def augment_chat_body_with_rag(body: dict[str, Any]) -> dict[str, Any]:
    if not settings.rag_enabled:
        return body

    if collection_count() == 0:
        return body

    messages = body.get("messages")
    if not isinstance(messages, list):
        return body

    query = _extract_last_user_text(messages)
    if not query:
        return body

    hits = await query_chunks(query, top_k=settings.rag_top_k)
    if not hits:
        return body

    context = format_context(hits, settings.rag_context_chars)
    rag_system = (
        "You are Chopus PrivateGPT running fully offline on the user's machine.\n"
        "Use ONLY the retrieved context below when answering factual questions about documents.\n"
        "Cite sources inline like [1] or [2] when you use them.\n"
        "If the context is insufficient, say you don't know from the local documents.\n"
        "Do not invent sources, tools, or web results.\n\n"
        f"Retrieved context:\n{context}"
    )

    augmented = dict(body)
    next_messages = [dict(message) for message in messages]

    if next_messages and next_messages[0].get("role") == "system":
        existing = next_messages[0].get("content")
        if isinstance(existing, str):
            next_messages[0]["content"] = f"{existing}\n\n{rag_system}"
        else:
            next_messages.insert(0, {"role": "system", "content": rag_system})
    else:
        next_messages.insert(0, {"role": "system", "content": rag_system})

    augmented["messages"] = next_messages
    # Non-breaking hint for clients that want to show sources later
    augmented["_rag_sources"] = [
        {
            "index": i + 1,
            "source": hit.get("source"),
            "filename": hit.get("filename") or _short_source(str(hit.get("source", ""))),
            "similarity": hit.get("similarity"),
        }
        for i, hit in enumerate(hits)
    ]
    return augmented
