"""
Embeddings Module
Converts text chunks into vector embeddings
using Sentence Transformers

How text becomes vectors
Which embedding model is used
How semantic meaning is captured
Foundation of semantic search
"""

from typing import List
from sentence_transformers import SentenceTransformer # type: ignore
import config

# Load model once — stays in memory for whole session
_model = None


def get_model() -> SentenceTransformer:
    """
    Load embedding model (cached after first load)
    Second call returns instantly — no reloading

    Returns:
        SentenceTransformer model
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {config.EMBED_MODEL}")
        _model = SentenceTransformer(config.EMBED_MODEL)
        print(f"✅ Model loaded! Dimension: {_model.get_sentence_embedding_dimension()}")
    return _model


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    try:
        model = get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return []


def get_embeddings_batch(texts: List[str], show_progress: bool = True) -> List[List[float]]:
    """
    Generate embeddings for multiple texts
    Batch processing is much faster than one by one

    Args:
        texts: List of texts to embed
        show_progress: Whether to show progress bar

    Returns:
        List of embedding vectors
    """
    if show_progress:
        print(f"\nGenerating embeddings for {len(texts)} chunks...")
        print(f"Using model: {config.EMBED_MODEL}")

    try:
        model = get_model()

        # Batch encoding — processes 32 texts at once
        # Much faster than calling get_embedding() one by one
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        result = [emb.tolist() for emb in embeddings]

        if show_progress:
            print(f"✅ Generated {len(result)} embeddings")
            if result:
                print(f"Embedding dimension: {len(result[0])}")

        return result

    except Exception as e:
        print(f"Error generating batch embeddings: {str(e)}")
        return []


def embed_chunks(chunks: List[dict]) -> List[dict]:
    """
    Add embeddings to chunks

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Chunks with embeddings added
    """
    # Extract all texts first
    texts = [chunk['text'] for chunk in chunks]

    # Generate all embeddings in one batch (fast)
    embeddings = get_embeddings_batch(texts)

    # Add embeddings back to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding

    return chunks


# Test the module if run directly
if __name__ == "__main__":
    print("Testing Embeddings Module...\n")

    test_text = "Dialysis is a treatment for kidney failure."
    print(f"Test text: '{test_text}'")

    embedding = get_embedding(test_text)

    if embedding:
        print(f"✅ Embedding generated!")
        print(f"Dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print("❌ Failed to generate embedding")