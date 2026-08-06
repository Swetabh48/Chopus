from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "http://localhost:11434"
    host: str = "0.0.0.0"
    port: int = 8000

    # PrivateGPT-style local RAG
    rag_enabled: bool = True
    embedding_model: str = "nomic-embed-text"
    chroma_path: str = str(Path(__file__).resolve().parents[1] / "data" / "chroma")
    chunk_size: int = 900
    chunk_overlap: int = 140
    # Final chunks injected into the prompt
    rag_top_k: int = 4
    # Candidate pool pulled from vector search before BM25 fusion
    rag_fetch_k: int = 16
    # Drop weak vector hits (cosine similarity = 1 - distance)
    rag_min_similarity: float = 0.18
    # Keep prompt lean for faster local generation
    rag_context_chars: int = 3500
    rag_vector_weight: float = 0.6
    rag_hybrid: bool = True


settings = Settings()
