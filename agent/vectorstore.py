# agent/vectorstore.py
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

INDEX_PATH = "faiss.index"
META_PATH = "faiss_meta.json"
EMB_MODEL_NAME = "all-MiniLM-L6-v2"  # small & effective

class SimpleFAISSStore:
    def __init__(self, model_name=EMB_MODEL_NAME, index_path=INDEX_PATH, meta_path=META_PATH):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.metadatas = []  # list of dicts: {"source":..., "text":...}

    def build(self, docs):
        texts = []
        metas = []
        for d in docs:
            texts.append(d.page_content)
            md = getattr(d, "metadata", {}) or {}
            md_source = md.get("source") or md.get("file_path") or md.get("source", "local")
            metas.append({"source": md_source, "text": d.page_content[:200]})

        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.asarray(embeddings, dtype="float32"))

        faiss.write_index(index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(metas, f, ensure_ascii=False, indent=2)

        self.index = index
        self.metadatas = metas
        return True

    def load(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            return None
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.metadatas = json.load(f)
        return True

    def add_documents(self, docs):
        texts = [d.page_content for d in docs]
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.asarray(embeddings, dtype="float32"))
        for d in docs:
            md = getattr(d, "metadata", {}) or {}
            md_source = md.get("source") or md.get("file_path") or "local"
            self.metadatas.append({"source": md_source, "text": d.page_content[:200]})
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f, ensure_ascii=False, indent=2)

    def query(self, query_text, k=5):
        if self.index is None:
            raise RuntimeError("Index not loaded. Call build() or load().")
        q_emb = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(np.asarray(q_emb, dtype="float32"), k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.metadatas):
                continue
            meta = self.metadatas[idx]
            results.append({
                "score": float(score),
                "source": meta.get("source", "local"),
                "text_snippet": meta.get("text", "")
            })
        return results
