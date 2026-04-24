"""
Mem0 REST API Server - Self-hosted
Backend: ChromaDB (vetores) + Ollama (embeddings) + OpenRouter (extração de fatos)
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mem0 import Memory

app = FastAPI(title="Mem0 Self-Hosted", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração: OpenRouter como LLM, Ollama pra embeddings, ChromaDB pra vetores
config = {
    "llm": {
        "provider": "openai",  # OpenRouter é compatível com API OpenAI
        "config": {
            "model": os.getenv("MEM0_LLM_MODEL", "google/gemma-3-27b-it"),
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "openai_base_url": "https://openrouter.ai/api/v1",
            "temperature": 0.1,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "ai_memories",
            "host": os.getenv("CHROMA_HOST", "chromadb"),
            "port": int(os.getenv("CHROMA_PORT", "8000")),
        }
    }
}

# Inicializa a memória (lazy, conecta ao subir)
memory = Memory.from_config(config)


# ==============================================================
# SCHEMAS
# ==============================================================

class AddMemoryRequest(BaseModel):
    messages: list
    user_id: str = "default"
    agent_id: Optional[str] = None
    metadata: Optional[dict] = None

class SearchRequest(BaseModel):
    query: str
    user_id: str = "default"
    agent_id: Optional[str] = None
    limit: int = 5

class UpdateMemoryRequest(BaseModel):
    data: str


# ==============================================================
# ENDPOINTS (compatível com plugin openclaw-memory-mem0)
# ==============================================================

@app.get("/health")
async def health():
    return {"status": "ok", "service": "mem0-self-hosted"}

@app.post("/v1/memories")
async def add_memory(req: AddMemoryRequest):
    """Salva memórias a partir de mensagens de conversa."""
    try:
        result = memory.add(
            req.messages,
            user_id=req.user_id,
            agent_id=req.agent_id,
            metadata=req.metadata or {}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/memories")
async def get_all_memories(user_id: str = "default", agent_id: Optional[str] = None):
    """Lista todas as memórias de um usuário."""
    try:
        results = memory.get_all(user_id=user_id, agent_id=agent_id)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/memories/search")
async def search_memories(req: SearchRequest):
    """Busca semântica nas memórias."""
    try:
        results = memory.search(
            req.query,
            user_id=req.user_id,
            agent_id=req.agent_id,
            limit=req.limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Busca uma memória específica por ID."""
    try:
        result = memory.get(memory_id)
        if not result:
            raise HTTPException(status_code=404, detail="Memória não encontrada")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/v1/memories/{memory_id}")
async def update_memory(memory_id: str, req: UpdateMemoryRequest):
    """Atualiza uma memória existente."""
    try:
        result = memory.update(memory_id, req.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/v1/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Remove uma memória específica."""
    try:
        memory.delete(memory_id)
        return {"status": "deleted", "id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/v1/memories")
async def delete_all_memories(user_id: str = "default"):
    """Remove TODAS as memórias de um usuário. Cuidado!"""
    try:
        memory.delete_all(user_id=user_id)
        return {"status": "all memories deleted", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
