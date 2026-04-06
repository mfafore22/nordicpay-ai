import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import get_embedding_config, CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENTS_PATH, VECTOR_STORE_PATH


class RAGPipeline:
    def __init__(self):
        embedding_config = get_embedding_config()

        if embedding_config["backend"] == "openai":
            from langchain.embeddings.openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model=embedding_config["model"],
                openai_api_key=embedding_config["api_key"]
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_config["model"]
            )

        self.vector_store = None
        self._load_or_build()

    def _load_or_build(self):
        if os.path.exists(VECTOR_STORE_PATH):
            print(f"Loading existing vector store from {VECTOR_STORE_PATH}")
            self.vector_store = FAISS.load_local(
                VECTOR_STORE_PATH, self.embeddings, allow_dangerous_deserialization=True
            )
            print(f"Vector store loaded.")
        else:
            print("No vector store found. Building...")
            self.build()

    def build(self):
        if not os.path.exists(DOCUMENTS_PATH):
            os.makedirs(DOCUMENTS_PATH)
            print(f"Created {DOCUMENTS_PATH} — add your .txt files there and restart.")
            return

        loader = DirectoryLoader(DOCUMENTS_PATH, glob="**/*.txt")
        documents = loader.load()

        if not documents:
            print("No documents found.")
            return

        print(f"Loaded {len(documents)} documents")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")

        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.vector_store.save_local(VECTOR_STORE_PATH)
        print(f"Vector store saved to {VECTOR_STORE_PATH}")

    def retrieve(self, query, top_k=3):
        if not self.vector_store:
            return []
        docs = self.vector_store.similarity_search_with_score(query, k=top_k)
        return [
            {"text": doc.page_content, "score": round(float(1 / (1 + score)), 3), "source": doc.metadata.get("source", "")}
            for doc, score in docs
        ]

    def get_context(self, query, top_k=3):
        docs = self.retrieve(query, top_k)
        if not docs:
            return ""
        return "\n".join([d["text"] for d in docs])

    def doc_count(self):
        if not self.vector_store:
            return 0
        return self.vector_store.index.ntotal