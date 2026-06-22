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
    """
    Find all PDF files in the docs folder and subfolders
    
    Returns:
        List of dictionaries with 'path', 'filename', and 'category'
    """
    pdf_files = []
    docs_path = Path(config.PDF_FOLDER)
    
    # Check if docs folder exists
    if not docs_path.exists():
        print(f"Error: {config.PDF_FOLDER} folder not found!")
        return pdf_files
    
    # Walk through all subfolders
    for pdf_path in docs_path.rglob("*.pdf"):
        # Get category from parent folder name
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