"""
PDF Loader Module
Loads and extracts text from PDF files in the docs folder
"""

import os
from pathlib import Path
from typing import List, Dict
from PyPDF2 import PdfReader # type: ignore
import config

def get_all_pdf_files() -> List[Dict[str, str]]:
    pdf_files = []
    
    # Try multiple possible paths
    possible_paths = [
        Path(config.PDF_FOLDER),           # relative: docs/
        Path("/app/docs"),                  # HuggingFace absolute
        Path(__file__).parent / "docs",     # same folder as script
    ]
    
    docs_path = None
    for path in possible_paths:
        if path.exists():
            docs_path = path
            print(f"✅ Found docs folder at: {path}")
            break
    
    if docs_path is None:
        print("❌ docs folder not found in any location!")
        return pdf_files
    
    for pdf_path in docs_path.rglob("*.pdf"):
        category = pdf_path.parent.name if pdf_path.parent != docs_path else "general"
        pdf_files.append({
            "path": str(pdf_path),
            "filename": pdf_path.name,
            "category": category
        })
    
    print(f"Found {len(pdf_files)} PDF files")
    return pdf_files

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        # Extract text from each page
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num} ---\n"
                text += page_text
        
        return text
    
    except Exception as e:
        print(f" Error reading {pdf_path}: {str(e)}")
        return ""

def load_all_pdfs() -> List[Dict]:
    """
    Load all PDFs and extract their text
    
    Returns:
        List of dictionaries with PDF metadata and text
    """
    pdf_files = get_all_pdf_files()
    documents = []
    
    for pdf_info in pdf_files:
        print(f" Loading: {pdf_info['category']}/{pdf_info['filename']}")
        
        text = extract_text_from_pdf(pdf_info['path'])
        
        if text:
            documents.append({
                "text": text,
                "filename": pdf_info['filename'],
                "category": pdf_info['category'],
                "path": pdf_info['path']
            })
            print(f"    Extracted {len(text)} characters")
        else:
            print(f"     No text extracted")
    
    print(f"\n Successfully loaded {len(documents)} documents")
    return documents

# Test the module if run directly
if __name__ == "__main__":
    print("Testing PDF Loader...\n")
    docs = load_all_pdfs()
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    for doc in docs:
        print(f"Category: {doc['category']:15} | File: {doc['filename']}")