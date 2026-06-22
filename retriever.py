"""
Retriever Module
Searches the vector database for relevant chunks
how semantic search works
how embeddings are used
how relevant chunks are found
why RAG is “intelligent retrieval” instead of keyword search
"""

from typing import List, Dict
from embeddings import get_embedding
from vector_store import VectorStore
import config

class Retriever:
    """
    Handles retrieval of relevant document chunks
    """
    
    def __init__(self):
        """Initialize the retriever with vector store"""
        self.store = VectorStore()
        self.store.create_collection()
        print("✅ Retriever initialized")
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = config.TOP_K
        
        # Convert query to embedding
        print(f"\nSearching for: '{query}'")
        query_embedding = get_embedding(query)
        
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        # Search vector database
        results = self.store.search(query_embedding, top_k=top_k)
        
        # Format results
        chunks = []
        if results and results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                chunk = {
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                chunks.append(chunk)
            
            print(f"Found {len(chunks)} relevant chunks")
        else:
            print("⚠️  No results found")
        
        return chunks
    
    def retrieve_with_scores(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve chunks with similarity scores
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunks with similarity scores (0-1, higher is better)
        """
        chunks = self.retrieve(query, top_k)
        
        # Convert distance to similarity score
        # Lower distance = higher similarity
        for chunk in chunks:
            if chunk['distance'] is not None:
                # Convert distance to similarity (0-1 scale)
                # This is a simple inverse transformation
                similarity = 1 / (1 + chunk['distance'])
                chunk['similarity'] = similarity
            else:
                chunk['similarity'] = 0.0
        
        return chunks
    
    def format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context for LLM
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            text = chunk['text']
            
            # Format each chunk with metadata
            context_part = f"""
Source {i}: {metadata['category']}/{metadata['filename']}
{text}
"""
            context_parts.append(context_part)
        
        return "\n---\n".join(context_parts)
    
    def display_results(self, chunks: List[Dict]):
        """
        Display retrieval results in a readable format
        
        Args:
            chunks: Retrieved chunks
        """
        if not chunks:
            print("\n No results to display")
            return
        
        print("\n" + "="*70)
        print("RETRIEVAL RESULTS")
        print("="*70)
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            similarity = chunk.get('similarity', 0)
            
            print(f"\n[{i}] Category: {metadata['category']} | File: {metadata['filename']}")
            print(f"    Similarity: {similarity:.3f}")
            print(f"    Chunk: {metadata['chunk_id']}/{metadata['total_chunks']}")
            print(f"    Preview: {chunk['text'][:150]}...")
        
        print("\n" + "="*70)

# Test the module if run directly
if __name__ == "__main__":
    print("Testing Retriever...\n")
    
    # Initialize retriever
    retriever = Retriever()
    
    # Test queries
    test_queries = [
        "What foods should dialysis patients avoid?",
        "How does hemodialysis work?",
        "What is peritoneal dialysis?",
        "Emergency dialysis procedures"
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        
        # Retrieve with scores
        chunks = retriever.retrieve_with_scores(query, top_k=3)
        
        # Display results
        retriever.display_results(chunks)
        
        # Show formatted context
        print("\nFormatted Context for LLM:")
        print("-"*70)
        context = retriever.format_context(chunks)
        print(context[:500] + "...\n")