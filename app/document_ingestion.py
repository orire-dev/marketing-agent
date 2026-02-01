"""
Document ingestion and processing for RAG context
"""

import logging
import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import PyPDF2
from docx import Document
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A processed document chunk with embedding"""
    chunk_id: str
    doc_name: str
    doc_type: str
    section: Optional[str]
    page: Optional[int]
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None


class DocumentIngester:
    """Ingest and process documents for RAG"""
    
    def __init__(self, openai_api_key: Optional[str] = None, storage_path: str = "./documents"):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            logger.warning("OpenAI API key not found. Embeddings will not be generated.")
            self.openai_client = None
    
    def extract_text_from_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page numbers"""
        chunks = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    if text.strip():
                        chunks.append({
                            "text": text,
                            "page": page_num,
                            "section": None
                        })
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
        return chunks
    
    def extract_text_from_docx(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from DOCX with section detection"""
        chunks = []
        try:
            doc = Document(file_path)
            current_section = None
            current_text = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                # Detect headings (simple heuristic: bold or larger font)
                is_heading = para.style.name.startswith('Heading') or (
                    para.runs and para.runs[0].bold
                )
                
                if is_heading:
                    # Save previous section
                    if current_text:
                        chunks.append({
                            "text": "\n".join(current_text),
                            "page": None,
                            "section": current_section
                        })
                    current_section = text
                    current_text = [text]
                else:
                    current_text.append(text)
            
            # Save last section
            if current_text:
                chunks.append({
                    "text": "\n".join(current_text),
                    "page": None,
                    "section": current_section
                })
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
        return chunks
    
    def extract_text_from_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Split by double newlines (paragraphs)
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                return [{"text": p, "page": None, "section": None} for p in paragraphs]
        except Exception as e:
            logger.error(f"Error extracting TXT: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:  # Only if reasonable
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap  # Overlap for context
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",  # or "text-embedding-ada-002"
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def ingest_document(
        self,
        file_path: Path,
        doc_name: str,
        doc_type: str = "brand_book"
    ) -> List[DocumentChunk]:
        """
        Ingest a document and return processed chunks with embeddings.
        
        Args:
            file_path: Path to the document file
            doc_name: Name of the document
            doc_type: Type of document (brand_book, tone_guide, value_prop, etc.)
            
        Returns:
            List of DocumentChunk objects
        """
        logger.info(f"Ingesting document: {doc_name} ({doc_type})")
        
        # Extract text based on file type
        suffix = file_path.suffix.lower()
        if suffix == '.pdf':
            raw_chunks = self.extract_text_from_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            raw_chunks = self.extract_text_from_docx(file_path)
        elif suffix == '.txt':
            raw_chunks = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Process chunks
        document_chunks = []
        for raw_chunk in raw_chunks:
            # Further chunk if too long
            text_chunks = self.chunk_text(raw_chunk["text"], chunk_size=1000, overlap=200)
            
            for text_chunk in text_chunks:
                chunk_id = str(uuid.uuid4())
                
                # Generate embedding
                embedding = self.generate_embedding(text_chunk)
                
                document_chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    doc_type=doc_type,
                    section=raw_chunk.get("section"),
                    page=raw_chunk.get("page"),
                    text=text_chunk,
                    embedding=embedding,
                    metadata={
                        "doc_type": doc_type,
                        "section": raw_chunk.get("section"),
                        "page": raw_chunk.get("page")
                    }
                )
                document_chunks.append(document_chunk)
        
        logger.info(f"Created {len(document_chunks)} chunks from {doc_name}")
        return document_chunks
    
    def save_chunks(self, chunks: List[DocumentChunk], storage_file: str = "chunks.json"):
        """Save chunks to disk (simple JSON storage for now)"""
        import json
        storage_file_path = self.storage_path / storage_file
        
        # Load existing chunks
        existing_chunks = []
        if storage_file_path.exists():
            try:
                with open(storage_file_path, 'r') as f:
                    existing_chunks = json.load(f)
            except:
                existing_chunks = []
        
        # Add new chunks
        chunks_data = [
            {
                "chunk_id": c.chunk_id,
                "doc_name": c.doc_name,
                "doc_type": c.doc_type,
                "section": c.section,
                "page": c.page,
                "text": c.text,
                "embedding": c.embedding,
                "metadata": c.metadata
            }
            for c in chunks
        ]
        
        existing_chunks.extend(chunks_data)
        
        # Save
        with open(storage_file_path, 'w') as f:
            json.dump(existing_chunks, f, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks to {storage_file_path}")
