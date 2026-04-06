import os 
from dotenv import load_dotenv

load_dotenv()


# LLM API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


# Embedding config
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "huggingface")  
HUGGINGFACE_MODEL_SIZE = os.getenv("HUGGINGFACE_MODEL", "small")


HUGGINGFACE_MODELS = {
    "small": "sentence-transformers/all-MiniLM-L6-v2",
    "medium": "sentence-transformers/all-mpnet-base-v2",
    "large": "sentence-transformers/all-mpnet-large-v2",
}

OPENAI_EMBEDDING_MODEL = {
    "small": "text-embedding-3-small",
    "medium": "text-embedding-3-medium",
    "large": "text-embedding-3-large",
}

OPENAI_EMBEDDING_MODELS = os.getenv("OPENAI_EMBEDDING_MODEL", "small")


#Local model config
BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
LORA_ADAPTER_PATH = os.getenv("LORA_ADAPTER_PATH", "../nordic-bank-model")

# RAG config
DOCUMENTS_PATH = "./financial_docs"
VECTOR_STORE_PATH = "./faiss_index"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Generation config
MAX_TOKENS = 512
TEMPERATURE = 0.7

# Cache
CACHE_TTL = 3600

# System prompt used for all models
SYSTEM_PROMPT = """You are NordicPay banking assistant. Answer customer questions accurately and concisely based ONLY on the provided context. If the context doesn't contain the answer, say "I don't have information about that." Be professional and helpful."""


def get_available_models():
    """Return list of available model backends based on which API keys are set"""
    models = []
    
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-your"):
        models.append({
            "id": "openai",
            "name": "OpenAI GPT-4o-mini",
            "type": "api",
            "ready": True
        })
    
    if GROQ_API_KEY:  # ADD THIS BLOCK
        models.append({
            "id": "groq",
            "name": "Groq Llama 3.1 70B (Free)",
            "type": "api", 
            "ready": True
        })
    
    if os.path.exists(LORA_ADAPTER_PATH):
        models.append({
            "id": "local-lora",
            "name": "NordicPay Fine-tuned (Local)",
            "type": "local",
            "ready": True
        })
    
    return models

def get_embedding_config():
    if EMBEDDING_BACKEND == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        return {
            "backend": "openai",
            "model": OPENAI_EMBEDDING_MODELS.get(OPENAI_EMBEDDING_MODEL, "text-embedding-3-small"),
            "api_key": OPENAI_API_KEY
        }
    return {
        "backend": "huggingface",
        "model": HUGGINGFACE_MODELS.get(HUGGINGFACE_MODEL_SIZE, HUGGINGFACE_MODELS["small"])
    }