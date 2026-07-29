"""
Embeddings module for computing semantic embeddings using sentence-transformers.
"""
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Optional


# Global model cache
_model = None
_model_name = "all-MiniLM-L6-v2"


def get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Get or load the sentence-transformers model with caching.
    
    Args:
        model_name: Name of the model to load.
    
    Returns:
        SentenceTransformer model instance.
    """
    global _model, _model_name
    
    if _model is None or _model_name != model_name:
        print(f"Loading model: {model_name}")
        _model = SentenceTransformer(model_name)
        _model_name = model_name
        print("Model loaded successfully")
    
    return _model


def compute_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Compute embedding for a given text.
    
    Args:
        text: Text to embed.
        model_name: Name of the model to use.
    
    Returns:
        numpy array of embedding vectors.
    """
    model = get_model(model_name)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def compute_embeddings_batch(texts: list, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Compute embeddings for multiple texts in batch.
    
    Args:
        texts: List of texts to embed.
        model_name: Name of the model to use.
    
    Returns:
        numpy array of embedding vectors.
    """
    model = get_model(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


def save_embedding(embedding: np.ndarray, path: str) -> None:
    """
    Save embedding to a .npy file.
    
    Args:
        embedding: Embedding array to save.
        path: Path to save the embedding.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, embedding)


def load_embedding(path: str) -> np.ndarray:
    """
    Load embedding from a .npy file.
    
    Args:
        path: Path to the embedding file.
    
    Returns:
        numpy array of embedding vectors.
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"Embedding file not found: {path}")
    return np.load(path)


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector.
        embedding2: Second embedding vector.
    
    Returns:
        Cosine similarity score between 0 and 1.
    """
    # Normalize embeddings
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Compute cosine similarity
    similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
    return float(similarity)


def compute_similarities_batch(embedding: np.ndarray, embeddings_matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between one embedding and a matrix of embeddings.
    
    Args:
        embedding: Single embedding vector.
        embeddings_matrix: Matrix of embedding vectors (n_embeddings, dim).
    
    Returns:
        Array of similarity scores.
    """
    # Normalize the query embedding
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return np.zeros(len(embeddings_matrix))
    
    embedding_normalized = embedding / norm
    
    # Normalize all embeddings in matrix
    norms = np.linalg.norm(embeddings_matrix, axis=1)
    norms[norms == 0] = 1  # Avoid division by zero
    embeddings_normalized = embeddings_matrix / norms[:, np.newaxis]
    
    # Compute dot products
    similarities = np.dot(embeddings_normalized, embeddings_normalized.T)
    return similarities


if __name__ == "__main__":
    # Test embedding computation
    test_text = "This is a test sentence for embedding computation."
    embedding = compute_embedding(test_text)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {len(embedding)}")
    
    # Test save/load
    test_path = "cache/test_embedding.npy"
    save_embedding(embedding, test_path)
    loaded = load_embedding(test_path)
    print(f"Loaded embedding shape: {loaded.shape}")
    print(f"Embeddings match: {np.allclose(embedding, loaded)}")
    
    # Test similarity computation
    text1 = "Machine learning is a subset of artificial intelligence."
    text2 = "AI and ML are related fields in computer science."
    text3 = "The weather is nice today."
    
    emb1 = compute_embedding(text1)
    emb2 = compute_embedding(text2)
    emb3 = compute_embedding(text3)
    
    sim12 = compute_similarity(emb1, emb2)
    sim13 = compute_similarity(emb1, emb3)
    sim23 = compute_similarity(emb2, emb3)
    
    print(f"Similarity (text1, text2): {sim12:.4f}")
    print(f"Similarity (text1, text3): {sim13:.4f}")
    print(f"Similarity (text2, text3): {sim23:.4f}")
