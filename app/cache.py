import hashlib
import time
import json
import os

CACHE_FILE = "./response_cache.json"


class ResponseCache:
    def __init__(self, ttl=3600):
        self.ttl = ttl
        self.cache = self._load()

    def _load(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _key(self, model_id, question, context):
        raw = f"{model_id}|{question}|{context}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, model_id, question, context):
        key = self._key(model_id, question, context)
        entry = self.cache.get(key)
        if entry and time.time() - entry["ts"] < self.ttl:
            return entry["response"]
        if entry:
            del self.cache[key]
            self._save()
        return None

    def set(self, model_id, question, context, response):
        key = self._key(model_id, question, context)
        self.cache[key] = {
            "response": response,
            "ts": time.time(),
            "model": model_id,
            "question": question
        }
        self._save()

    def clear(self):
        self.cache = {}
        self._save()

    def stats(self):
        now = time.time()
        valid = sum(1 for v in self.cache.values() if now - v["ts"] < self.ttl)
        return {"total": len(self.cache), "valid": valid}