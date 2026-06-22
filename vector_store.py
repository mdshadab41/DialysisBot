"""
Vector Store Module
Stores and retrieves embeddings using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict
import os
import config

class VectorStore:
    """
    Manages the ChromaDB vector database
    """
    
    def __init__(self):
        """Initialize ChromaDB client"""
        # Create chroma_db folder if it doesn't exist
        os.makedirs(config.CHROMA_DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Collection name
        self.collection_name = "dialysis_docs"
        
        print(f"ChromaDB initialized at: {config.CHROMA_DB_PATH}")
    
    def create_collection(self, reset: bool = False):
        """
        Create or get the collection
        
        Args:
            reset: If True, delete existing collection and create new
        """
        if reset:
            try:
                self.client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Dialysis medical documents"}
        )
        
        count = self.collection.count()
        print(f"Collection '{self.collection_name}' ready ({count} documents)")
        
        return self.collection
    
    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks with embeddings to the database
        
        Args:
            chunks: List of chunks with text, metadata, and embeddings
        """
        if not hasattr(self, 'collection'):
            self.create_collection()
        
        print(f"\nAdding {len(chunks)} chunks to vector database...")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{chunk['category']}_{chunk['filename']}_{chunk['chunk_id']}"
            ids.append(chunk_id)
            
            # Text content
            documents.append(chunk['text'])
            
            # Embedding vector
            embeddings.append(chunk['embedding'])
            
            # Metadata
            metadata = {
                'filename': chunk['filename'],
                'category': chunk['category'],
                'chunk_id': str(chunk['chunk_id']),
                'total_chunks': str(chunk['total_chunks']),
                'source': chunk['source']
            }
            metadatas.append(metadata)
        
        # Add to collection in batches
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            self.collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                embeddings=embeddings[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            
            print(f"   Added batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")
        
        print(f"Successfully added {len(chunks)} chunks")
        print(f"Total documents in database: {self.collection.count()}")
    
    def search(self, query_embedding: List[float], top_k: int = None) -> Dict:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            
        Returns:
            Dictionary with results
        """
        if top_k is None:
            top_k = config.TOP_K
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results
    
    def get_stats(self):
        """Get database statistics"""
        if not hasattr(self, 'collection'):
            self.create_collection()
        
        total = self.collection.count()
        
        print("\n" + "="*50)
        print("VECTOR DATABASE STATISTICS")
        print("="*50)
        print(f"Total chunks: {total}")
        print(f"Collection: {self.collection_name}")
        print(f"Path: {config.CHROMA_DB_PATH}")
        print("="*50)

# Test the module if run directly
if __name__ == "__main__":
    from pdf_loader import load_all_pdfs
    from text_splitter import split_documents
    from embeddings import embed_chunks
    
    print("Testing Vector Store...\n")
    
    # Load and process documents
    print("Step 1: Loading PDFs...")
    documents = load_all_pdfs()
    
    print("\nStep 2: Splitting into chunks...")
    chunks = split_documents(documents)
    
    print("\nStep 3: Generating embeddings...")
    chunks = embed_chunks(chunks)
    
    print("\nStep 4: Creating vector database...")
    store = VectorStore()
    store.create_collection(reset=True)
    store.add_chunks(chunks)
    
    # Show stats
    store.get_stats()
    
    print("\nVector database created successfully!")