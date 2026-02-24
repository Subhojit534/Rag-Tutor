"""
Embeddings Module - MiniLM for Text Embeddings
"""
from typing import List
from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Get cached embedding model.
    Uses all-MiniLM-L6-v2 for efficient embeddings.
    """
    return SentenceTransformer('all-MiniLM-L6-v2')


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for a single query.
    
    Args:
        query: Query text
        
    Returns:
        Embedding vector
    """
    model = get_embedding_model()
    embedding = model.encode([query], convert_to_numpy=True)
    return embedding[0].tolist()
