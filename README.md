# NordicPay AI Banking Assistant

A RAG-powered banking assistant that answers customer questions using constrained documentation and multiple LLM backends.

---

## 1. What Did You Build and Why?

**What:** A conversational AI assistant for banking customers that answers questions about accounts, cards, loans, and policies.

**Why:** Traditional FAQ pages require manual searching. This solution provides natural language interaction with accurate, source-cited answers from banking documentation.

**Key capabilities:**
- Answers questions strictly from provided documents (no hallucination)
- Shows confidence scores and source citations
- Supports multiple LLM backends (Groq API for speed, local fine-tuned model for privacy)
- Handles uncertainty explicitly ("I don't have information about that")

---

## 2. How Does the Solution Work?

```
User Question
     |
     v
+--------------------+
|   RAG Pipeline     |  --> Retrieves relevant document chunks
+--------------------+
     |
     v
+--------------------+
|   LLM Generation   |  --> Generates answer from context
+--------------------+
     |
     v
Response + Sources + Confidence
```

**Components:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | SvelteKit | Chat interface with model selection |
| Backend | FastAPI | API routing, caching, RAG pipeline |
| Vector Store | FAISS | Semantic document search |
| Embeddings | sentence-transformers | Local, free embeddings |
| LLM (API) | Groq Llama 3.1 | Fast responses (2-5 seconds) |
| LLM (Local) | TinyLlama + LoRA | Privacy-preserving, fine-tuned |

**Data flow:**
1. User submits question
2. RAG retrieves top-3 relevant document chunks
3. Context + question sent to selected LLM
4. Response displayed with confidence score and sources

---

## 3. Key Technical Decisions

### Decision 1: RAG + Fine-tuning (not just one)

| Approach | Chose? | Reasoning |
|----------|--------|-----------|
| Pure RAG | No | Relies entirely on retrieval quality |
| Pure Fine-tuning | No | Hard to update, hallucination risk |
| Combined | Yes | RAG provides facts, fine-tuning teaches tone/format |

### Decision 2: TinyLlama 1.1B for local model

- Runs on CPU (no GPU required)
- Small enough for demonstration
- LoRA fine-tuning keeps adapter size small (~9MB)
- Tradeoff: Slower inference (1-5 minutes on CPU)

### Decision 3: Groq as primary API

- Free tier available
- Fast inference (2-5 seconds)
- OpenAI-compatible API
- Tradeoff: Data sent to external server

### Decision 4: FAISS for vector store

- No external database needed
- Fast similarity search
- Persists to disk
- Tradeoff: Memory-based, not suitable for millions of documents

### Decision 5: Response caching

- Reduces API costs for repeated queries
- Instant responses for cached questions
- Cache key: hash(model + question + context)

---

## 4. Where Can This Solution Fail?

| Failure Mode | Cause | Mitigation |
|--------------|-------|------------|
| Wrong answer | Relevant document not retrieved | Confidence score warns user; increase top_k |
| Hallucination | LLM generates beyond context | System prompt instructs strict adherence |
| Slow response | Local model on CPU | Use Groq API; show "Thinking..." indicator |
| Outdated info | Documents not updated | Easy document update via RAG rebuild |
| Out of scope questions | User asks non-banking questions | Explicit "I don't have information" response |
| API rate limits | Too many Groq requests | Caching reduces repeat calls |

**Specific limitations:**
- Local model takes 1-10 minutes on CPU (no GPU)
- Only answers from provided documents (by design)
- No multi-turn conversation memory (stateless)
- No authentication (demonstration only)

---

## 5. What Would You Do for Production?

### Immediate (Week 1-2)
- Add authentication (OAuth/JWT)
- GPU inference for local model (5-10 seconds vs 5-10 minutes)
- Streaming responses for better UX
- Logging and monitoring

### Short-term (Month 1)
- Multi-turn conversation memory
- Hybrid search (semantic + keyword)
- User feedback collection (thumbs up/down)
- Rate limiting and abuse prevention

### Medium-term (Month 2-3)
- A/B testing different models
- Fine-tune on more data (500+ examples vs current 15)
- Query rewriting for better retrieval
- Analytics dashboard

### Security hardening
- PII detection and removal before API calls
- Audit logging
- Input sanitization
- HTTPS/TLS

---

## Running the Solution

### Quick Start (Docker)

```bash
# 1. Clone and configure
cd Op-ai
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 2. Start
docker-compose up

# 3. Access
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

### Manual Start

```bash
# Terminal 1: Backend
cd Op-ai
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd Op-ai/frontend
npm install
npm run dev
```

### Test

```bash
# Health check
curl http://localhost:8000/api/health

# Ask a question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the monthly fee for Plus?", "model_id": "groq"}'
```

---

## Project Structure

```
Op-ai/
├── app/
│   ├── main.py           # FastAPI routes
│   ├── config.py         # Configuration
│   ├── model_manager.py  # LLM routing
│   ├── rag_setup.py      # RAG pipeline
│   └── cache.py          # Response caching
├── frontend/             # SvelteKit chat UI
├── financial_docs/       # Banking documents (RAG source)
├── nordic-bank-model/    # Fine-tuned LoRA adapter
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Requirements Fulfilled

| Requirement | Implementation |
|-------------|----------------|
| Way to ask questions | SvelteKit web UI |
| LLM usage | Groq API + Local fine-tuned model |
| Constrained data source | 4 documents in RAG |
| Answer source tracking | Sources with relevance % |
| Uncertainty handling | Confidence scores + "I don't have info" |
| BONUS: Agent structure | Reasoning steps displayed |
| BONUS: Prompts described | System prompt in config.py |
| BONUS: Easy to extend | Modular architecture, Docker support |