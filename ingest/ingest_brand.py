#!/usr/bin/env python3
"""
Ingest brand book, tone guide, and value proposition documents
"""

import argparse
import logging
from pathlib import Path
from typing import List
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_document(text: str, doc_name: str, doc_type: str) -> List[dict]:
    """
    Chunk document using semantic (heading-based) and fixed-size fallback.
    
    Returns list of chunk dicts with:
    - chunk_id, doc_name, doc_type, section, page, chunk_text, chunk_index
    """
    chunks = []
    
    # Simple semantic chunking: split by headings (lines starting with # or all caps)
    lines = text.split('\n')
    current_section = None
    current_chunk_text = []
    chunk_index = 0
    
    for i, line in enumerate(lines):
        # Detect section headers
        if line.strip().startswith('#') or (line.isupper() and len(line.strip()) > 3 and len(line.strip()) < 50):
            # Save previous chunk
            if current_chunk_text:
                chunk_text = '\n'.join(current_chunk_text).strip()
                if chunk_text:
                    chunk_id = hashlib.md5(f"{doc_name}_{chunk_index}".encode()).hexdigest()
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_name": doc_name,
                        "doc_type": doc_type,
                        "section": current_section,
                        "page": None,  # Would need PDF parsing for page numbers
                        "chunk_text": chunk_text,
                        "chunk_index": chunk_index,
                        "metadata": {}
                    })
                    chunk_index += 1
            
            # Start new chunk
            current_section = line.strip()
            current_chunk_text = [line]
        else:
            current_chunk_text.append(line)
            
            # Fixed-size fallback: if chunk gets too long, split it
            if len('\n'.join(current_chunk_text)) > 1000:
                chunk_text = '\n'.join(current_chunk_text[:-1]).strip()
                if chunk_text:
                    chunk_id = hashlib.md5(f"{doc_name}_{chunk_index}".encode()).hexdigest()
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_name": doc_name,
                        "doc_type": doc_type,
                        "section": current_section,
                        "page": None,
                        "chunk_text": chunk_text,
                        "chunk_index": chunk_index,
                        "metadata": {}
                    })
                    chunk_index += 1
                    current_chunk_text = [current_chunk_text[-1]]
    
    # Save final chunk
    if current_chunk_text:
        chunk_text = '\n'.join(current_chunk_text).strip()
        if chunk_text:
            chunk_id = hashlib.md5(f"{doc_name}_{chunk_index}".encode()).hexdigest()
            chunks.append({
                "chunk_id": chunk_id,
                "doc_name": doc_name,
                "doc_type": doc_type,
                "section": current_section,
                "page": None,
                "chunk_text": chunk_text,
                "chunk_index": chunk_index,
                "metadata": {}
            })
    
    return chunks


def read_pdf(filepath: Path) -> str:
    """Read text from PDF file"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(filepath))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except ImportError:
        logger.error("pypdf not installed. Install with: pip install pypdf")
        raise
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise


def read_docx(filepath: Path) -> str:
    """Read text from DOCX file"""
    try:
        from docx import Document
        doc = Document(str(filepath))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        logger.error("python-docx not installed. Install with: pip install python-docx")
        raise
    except Exception as e:
        logger.error(f"Error reading DOCX: {e}")
        raise


def read_text(filepath: Path) -> str:
    """Read plain text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def ingest_document(filepath: Path, doc_type: str) -> List[dict]:
    """Ingest a single document"""
    logger.info(f"Ingesting {filepath} as {doc_type}")
    
    # Read based on file extension
    ext = filepath.suffix.lower()
    if ext == '.pdf':
        text = read_pdf(filepath)
    elif ext == '.docx':
        text = read_docx(filepath)
    elif ext in ['.txt', '.md']:
        text = read_text(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Chunk the document
    doc_name = filepath.stem
    chunks = chunk_document(text, doc_name, doc_type)
    
    logger.info(f"Created {len(chunks)} chunks from {doc_name}")
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Ingest brand documents")
    parser.add_argument("--brandbook", type=Path, help="Path to brand book PDF/DOCX")
    parser.add_argument("--tone", type=Path, help="Path to tone guide PDF/DOCX")
    parser.add_argument("--valueprop", type=Path, help="Path to value proposition document")
    parser.add_argument("--output", type=Path, default=Path("chunks.json"), help="Output JSON file")
    
    args = parser.parse_args()
    
    all_chunks = []
    
    if args.brandbook:
        chunks = ingest_document(args.brandbook, "brand_book")
        all_chunks.extend(chunks)
    
    if args.tone:
        chunks = ingest_document(args.tone, "tone_guide")
        all_chunks.extend(chunks)
    
    if args.valueprop:
        chunks = ingest_document(args.valueprop, "value_prop")
        all_chunks.extend(chunks)
    
    if not all_chunks:
        logger.warning("No documents ingested. Provide --brandbook, --tone, or --valueprop")
        return
    
    # Save chunks (TODO: Write to Databricks)
    import json
    with open(args.output, 'w') as f:
        json.dump(all_chunks, f, indent=2)
    
    logger.info(f"Saved {len(all_chunks)} chunks to {args.output}")
    logger.info("TODO: Upload chunks to Databricks brand_assets table and create embeddings")


if __name__ == "__main__":
    main()
