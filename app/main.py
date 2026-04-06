from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.model_manager import ModelManager
from app.rag_setup import RAGPipeline
from app.cache import ResponseCache
from app.config import CACHE_TTL, get_available_models
import time


rag = RAGPipeline()
models = ModelManager()
cache = ResponseCache(ttl=CACHE_TTL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("NordicPay AI backend starting...")
    print(f"Available models: {[m['id'] for m in get_available_models()]}")
    print(f"RAG documents: {rag.doc_count()}")
    yield

app = FastAPI(title="NordicPay AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    model_id: str = "local-lora"
    use_rag: bool = True
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    model_used: str
    from_cache: bool
    sources: list = []
    reasoning: list = []
    latency_ms: int = 0


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start = time.time()

    # RAG retrieval (skip for greetings)
    context = ""
    sources = []
    
    # Check if it's a greeting - skip RAG
    greetings = ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening"]
    is_greeting = req.question.lower().strip().rstrip("!?.") in greetings
    
    if req.use_rag and not is_greeting:
        sources = rag.retrieve(req.question, req.top_k)
        context = "\n".join([s["text"] for s in sources])

    # Cache check (skip for greetings)
    if not is_greeting:
        cached = cache.get(req.model_id, req.question, context)
        if cached:
            return ChatResponse(
                answer=cached,
                model_used=req.model_id,
                from_cache=True,
                sources=sources,
                reasoning=[{"step": 1, "action": "Cache hit", "detail": "Returning cached response"}],
                latency_ms=int((time.time() - start) * 1000)
            )

    # Generate
    try:
        result = models.generate(req.model_id, req.question, context)
        
        # Handle both old (string) and new (dict) return format
        if isinstance(result, dict):
            answer = result["answer"]
            reasoning = result.get("reasoning", [])
        else:
            answer = result
            reasoning = []
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    # Cache store (skip for greetings)
    if not is_greeting:
        cache.set(req.model_id, req.question, context, answer)

    return ChatResponse(
        answer=answer,
        model_used=req.model_id,
        from_cache=False,
        sources=sources,
        reasoning=reasoning,
        latency_ms=int((time.time() - start) * 1000)
    )


@app.get("/api/models")
async def list_models():
    return {"models": get_available_models()}


@app.get("/api/cache/stats")
async def cache_stats():
    return cache.stats()


@app.post("/api/cache/clear")
async def clear_cache():
    cache.clear()
    return {"status": "cleared"}


@app.get("/api/rag/stats")
async def rag_stats():
    return {"documents": rag.doc_count()}


@app.post("/api/rag/rebuild")
async def rebuild_rag():
    rag.build()
    return {"status": "rebuilt", "documents": rag.doc_count()}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "models": [m["id"] for m in get_available_models()],
        "rag_docs": rag.doc_count()
    }