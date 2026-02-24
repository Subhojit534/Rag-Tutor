"""
Vector Store Module - FAISS for Subject-wise Indexing
Files stored on disk, index paths managed per subject.
"""
import os
import json
import faiss
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from app.config import settings
from app.ai.embeddings import embed_texts, embed_query


class SubjectVectorStore:
    """
    FAISS-based vector store for a single subject.
    Each subject has its own isolated index.
    """
    
    def __init__(self, subject_id: int):
        self.subject_id = subject_id
        self.index_dir = settings.faiss_path / f"subject_{subject_id}"
        self.index_path = self.index_dir / "index.faiss"
        self.metadata_path = self.index_dir / "metadata.json"
        self.index: Optional[faiss.IndexFlatL2] = None
        self.metadata: List[Dict] = []
        self._load_or_create()
    
    def _load_or_create(self):
        """Load existing index or create new one."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        if self.index_path.exists() and self.metadata_path.exists():
            # Load existing
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            # Create new - 384 dimensions for MiniLM
            self.index = faiss.IndexFlatL2(384)
            self.metadata = []
    
    def add_documents(self, chunks: List[Dict]):
        """
        Add document chunks to the index.
        
        Args:
            chunks: List of {"text": str, "source": str, "page": int}
        """
        if not chunks:
            return
        
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)
        
        # Add to FAISS
        vectors = np.array(embeddings, dtype=np.float32)
        self.index.add(vectors)
        
        # Save metadata
        for chunk in chunks:
            self.metadata.append({
                "text": chunk["text"],
                "source": chunk.get("source", "Unknown"),
                "page": chunk.get("page", 0)
            })
        
        self._save()
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of matching documents with scores
        """
        if self.index.ntotal == 0:
            return []
        
        query_embedding = embed_query(query)
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["score"] = float(dist)
                result["rank"] = i + 1
                results.append(result)
        
        return results
    
    def _save(self):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    
    def clear(self):
        """Clear the entire index (for re-indexing)."""
        self.index = faiss.IndexFlatL2(384)
        self.metadata = []
        self._save()
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "subject_id": self.subject_id,
            "total_chunks": self.index.ntotal,
            "unique_sources": len(set(m.get("source", "") for m in self.metadata))
        }


def get_vector_store(subject_id: int) -> SubjectVectorStore:
    """Get or create vector store for a subject."""
    return SubjectVectorStore(subject_id)


def reindex_subject(subject_id: int, chunks: List[Dict]):
    """
    Re-index a subject's FAISS store.
    Called when PDFs are added/removed.
    
    Args:
        subject_id: Subject ID
        chunks: All chunks for this subject
    """
    store = SubjectVectorStore(subject_id)
    store.clear()
    store.add_documents(chunks)
    return store.get_stats()
