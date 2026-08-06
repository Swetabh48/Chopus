from fastapi import FastAPI

from app.routes import chat, health, models, rag

app = FastAPI(
    title="Chopus Local AI",
    description="PrivateGPT-style local AI: Ollama chat + document RAG",
    version="0.2.0",
)

app.include_router(health.router)
app.include_router(models.router)
app.include_router(chat.router)
app.include_router(rag.router)
