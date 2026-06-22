"""
PDF Manager Module
Handles uploading and managing PDF documents
"""

import os
from pathlib import Path
from typing import List
from PyPDF2 import PdfReader # type: ignore
import config

def save_uploaded_pdf(uploaded_file, category: str = "uploaded") -> dict:
    """
    Save an uploaded PDF file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        category: Category folder name
        
    Returns:
        Dictionary with success status and message
    """
    try:
        # Create category folder if it doesn't exist
        category_path = Path(config.PDF_FOLDER) / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = category_path / uploaded_file.name
        
        # Check if file already exists
        if file_path.exists():
            return {
                'success': False,
                'message': f'File "{uploaded_file.name}" already exists',
                'path': None
            }
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Verify it's a valid PDF
        try:
            reader = PdfReader(str(file_path))
            num_pages = len(reader.pages)
        except Exception as e:
            # Delete invalid file
            file_path.unlink()
            return {
                'success': False,
                'message': f'Invalid PDF file: {str(e)}',
                'path': None
            }
        
        return {
            'success': True,
            'message': f'Successfully uploaded "{uploaded_file.name}" ({num_pages} pages)',
            'path': str(file_path)
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error uploading file: {str(e)}',
            'path': None
        }

def list_all_pdfs() -> List[dict]:
    """
    List all PDF files in the docs folder
    
    Returns:
        List of PDF info dictionaries
    """
    pdfs = []
    docs_path = Path(config.PDF_FOLDER)
    
    if not docs_path.exists():
        return pdfs
    
    for pdf_path in docs_path.rglob("*.pdf"):
        category = pdf_path.parent.name if pdf_path.parent != docs_path else "general"
        
        # Get file size
        size_bytes = pdf_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        pdfs.append({
            'name': pdf_path.name,
            'category': category,
            'path': str(pdf_path),
            'size_mb': round(size_mb, 2)
        })
    
    return sorted(pdfs, key=lambda x: (x['category'], x['name']))

def delete_pdf(file_path: str) -> dict:
    """
    Delete a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with success status and message
    """
    try:
        pdf_path = Path(file_path)
        
        if not pdf_path.exists():
            return {
                'success': False,
                'message': 'File not found'
            }
        
        pdf_path.unlink()
        
        return {
            'success': True,
            'message': f'Deleted "{pdf_path.name}"'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error deleting file: {str(e)}'
        }

def rebuild_vector_database():
    """
    Rebuild the vector database with all current PDFs
    
    Returns:
        Dictionary with success status and statistics
    """
    try:
        from pdf_loader import load_all_pdfs
        from text_splitter import split_documents
        from embeddings import embed_chunks
        from vector_store import VectorStore
        
        print("\n🔄 Rebuilding vector database...")
        
        # Load all PDFs
        documents = load_all_pdfs()
        
        if not documents:
            return {
                'success': False,
                'message': 'No PDF documents found',
                'stats': {}
            }
        
        # Split into chunks
        chunks = split_documents(documents)
        
        # Generate embeddings
        chunks = embed_chunks(chunks)
        
        # Rebuild database
        store = VectorStore()
        store.create_collection(reset=True)
        store.add_chunks(chunks)
        
        return {
            'success': True,
            'message': 'Vector database rebuilt successfully',
            'stats': {
                'documents': len(documents),
                'chunks': len(chunks)
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error rebuilding database: {str(e)}',
            'stats': {}
        }