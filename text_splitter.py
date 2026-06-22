"""
Text Splitter Module
Splits documents into chunks using recursive strategy

This is VERY important in RAG because:

embeddings work better on smaller text
retrieval becomes more accurate
LLM context becomes manageable

Without chunking:

retrieval quality becomes poor
embeddings become too broad
context becomes noisy

"""

from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config

def create_text_splitter():
    """
    Create a recursive text splitter configured for medical documents
    
    Returns:
        RecursiveCharacterTextSplitter object
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=config.CHUNK_SEPARATORS,
        length_function=len,
        is_separator_regex=False
    )
    
    return splitter

def split_documents(documents: List[Dict]) -> List[Dict]:
    """
    Split documents into smaller chunks
    
    Args:
        documents: List of documents with 'text', 'filename', 'category'
        
    Returns:
        List of chunks with metadata
    """
    splitter = create_text_splitter()
    all_chunks = []
    
    print("\nSplitting documents into chunks...")
    print(f"Chunk size: {config.CHUNK_SIZE} characters")
    print(f"Overlap: {config.CHUNK_OVERLAP} characters\n")
    
    for doc in documents:
        # Split the text
        text_chunks = splitter.split_text(doc['text'])
        
        print(f"{doc['category']}/{doc['filename']}")
        print(f"   Original: {len(doc['text'])} chars → {len(text_chunks)} chunks")
        
        # Add metadata to each chunk
        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                "text": chunk_text,
                "filename": doc['filename'],
                "category": doc['category'],
                "chunk_id": i + 1,
                "total_chunks": len(text_chunks),
                "source": f"{doc['category']}/{doc['filename']}"
            }
            all_chunks.append(chunk)
    
    print(f"\nCreated {len(all_chunks)} total chunks from {len(documents)} documents")
    
    return all_chunks

def analyze_chunks(chunks: List[Dict]):
    """
    Analyze and display statistics about the chunks
    
    Args:
        chunks: List of text chunks
    """
    if not chunks:
        print("No chunks to analyze")
        return
    
    # Calculate statistics
    chunk_sizes = [len(chunk['text']) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    min_size = min(chunk_sizes)
    max_size = max(chunk_sizes)
    
    # Count chunks per category
    category_counts = {}
    for chunk in chunks:
        cat = chunk['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Display results
    print("\n" + "="*50)
    print("CHUNK ANALYSIS")
    print("="*50)
    print(f"Total chunks: {len(chunks)}")
    print(f"Average size: {avg_size:.0f} characters")
    print(f"Min size: {min_size} characters")
    print(f"Max size: {max_size} characters")
    print("\nChunks per category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category:15} : {count} chunks")
    print("="*50)

# Test the module if run directly
if __name__ == "__main__":
    from pdf_loader import load_all_pdfs
    
    print("Testing Text Splitter...\n")
    
    # Load PDFs
    documents = load_all_pdfs()
    
    if documents:
        # Split into chunks
        chunks = split_documents(documents)
        
        # Analyze results
        analyze_chunks(chunks)
        
        # Show a sample chunk
        if chunks:
            print("\n" + "="*50)
            print("SAMPLE CHUNK")
            print("="*50)
            sample = chunks[0]
            print(f"Category: {sample['category']}")
            print(f"File: {sample['filename']}")
            print(f"Chunk: {sample['chunk_id']}/{sample['total_chunks']}")
            print(f"Text preview (first 300 chars):")
            print("-"*50)
            print(sample['text'][:300] + "...")
            print("="*50)