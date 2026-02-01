"""
RAG (Retrieval Augmented Generation) module for brand/tone/product/segment retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A retrieved document chunk"""
    chunk_id: str
    doc_name: str
    doc_type: str
    section: Optional[str]
    page: Optional[int]
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None  # Relevance score


class RAGRetriever:
    """
    Retrieves relevant chunks from brand assets, products, segments.
    
    Supports both uploaded documents and stub data.
    """
    
    def __init__(self, databricks_config: Optional[Dict[str, Any]] = None):
        self.databricks_config = databricks_config
        self.uploaded_chunks = []  # Store uploaded document chunks
        # TODO: Initialize Databricks Vector Search client
    
    def add_documents(self, chunks: List[Any]):
        """Add uploaded document chunks to the retriever"""
        self.uploaded_chunks.extend(chunks)
        logger.info(f"Added {len(chunks)} chunks. Total: {len(self.uploaded_chunks)}")
    
    def _search_uploaded_chunks(self, query: str, doc_type: Optional[str] = None, top_k: int = 5) -> List[Chunk]:
        """Search uploaded chunks using simple text matching (can be upgraded to semantic search)"""
        if not self.uploaded_chunks:
            return []
        
        # Simple keyword matching (can be upgraded to use embeddings)
        query_lower = query.lower()
        scored_chunks = []
        
        for chunk in self.uploaded_chunks:
            if doc_type and chunk.doc_type != doc_type:
                continue
            
            # Simple relevance scoring
            text_lower = chunk.text.lower()
            score = text_lower.count(query_lower) * 10
            
            # Check if query words appear
            query_words = query_lower.split()
            for word in query_words:
                if word in text_lower:
                    score += 1
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to Chunk objects
        results = []
        for chunk, score in scored_chunks[:top_k]:
            results.append(Chunk(
                chunk_id=chunk.chunk_id,
                doc_name=chunk.doc_name,
                doc_type=chunk.doc_type,
                section=chunk.section,
                page=chunk.page,
                text=chunk.text,
                metadata=chunk.metadata or {},
                score=score
            ))
        
        return results
    
    def retrieve_brand_chunks(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieve brand book, tone guide, or value prop chunks.
        
        Args:
            query: Search query
            doc_types: Filter by doc type ('brand_book', 'tone_guide', 'value_prop')
            top_k: Number of chunks to return
            
        Returns:
            List of relevant chunks
        """
        logger.info(f"Retrieving brand chunks for query: {query}")
        
        # First, try to get chunks from uploaded documents
        uploaded_results = []
        if doc_types:
            for doc_type in doc_types:
                uploaded_results.extend(self._search_uploaded_chunks(query, doc_type, top_k))
        else:
            uploaded_results = self._search_uploaded_chunks(query, None, top_k)
        
        if uploaded_results:
            logger.info(f"Found {len(uploaded_results)} chunks from uploaded documents")
            return uploaded_results[:top_k]
        
        # Fallback to stub chunks if no uploaded documents
        logger.info("No uploaded documents found, using stub chunks")
        stub_chunks = [
            Chunk(
                chunk_id="brand_001",
                doc_name="eToro Brand Book 2024",
                doc_type="brand_book",
                section="Visual Identity",
                page=12,
                text="eToro brand colors: Primary blue (#1E88E5), Secondary green (#4CAF50). Typography: Use bold, modern sans-serif. Maintain high contrast for accessibility.",
                metadata={"section": "Visual Identity", "page": 12}
            ),
            Chunk(
                chunk_id="tone_001",
                doc_name="Tone of Voice Guide",
                doc_type="tone_guide",
                section="Core Principles",
                page=3,
                text="eToro voice: Friendly yet professional. Empower users with knowledge. Avoid financial jargon. Use clear, confident language. Never make promises or guarantees.",
                metadata={"section": "Core Principles", "page": 3}
            ),
            Chunk(
                chunk_id="value_001",
                doc_name="Value Proposition",
                doc_type="value_prop",
                section="Core Pillars",
                page=1,
                text="eToro value pillars: 1) Social trading - learn from others, 2) Accessible investing - start small, 3) Diverse assets - crypto, stocks, ETFs in one platform.",
                metadata={"section": "Core Pillars", "page": 1}
            )
        ]
        
        # Filter by doc_types if specified
        if doc_types:
            stub_chunks = [c for c in stub_chunks if c.doc_type in doc_types]
        
        return stub_chunks[:top_k]
    
    def retrieve_product_info(
        self,
        product_scope: str,
        top_k: int = 3
    ) -> List[Chunk]:
        """Retrieve product catalog information"""
        logger.info(f"Retrieving product info for: {product_scope}")
        
        # TODO: Query product_catalog table
        stub_chunks = [
            Chunk(
                chunk_id="product_crypto_001",
                doc_name="Product Catalog",
                doc_type="product",
                section="Crypto",
                page=None,
                text=f"Product: {product_scope}. Features: Trade 70+ cryptocurrencies, 24/7 trading, copy trading available. Required disclaimers: 'Crypto assets are highly volatile. Your capital is at risk.' Prohibited: No promises of returns, no guarantees.",
                metadata={"product_type": product_scope}
            )
        ]
        
        return stub_chunks[:top_k]
    
    def retrieve_segment_info(
        self,
        segment_id: Optional[str] = None,
        top_k: int = 2
    ) -> List[Chunk]:
        """Retrieve segment/persona information"""
        logger.info(f"Retrieving segment info: {segment_id}")
        
        # TODO: Query segments table
        if segment_id:
            stub_chunks = [
                Chunk(
                    chunk_id=f"segment_{segment_id}_001",
                    doc_name="Segments",
                    doc_type="segment",
                    section=segment_id,
                    page=None,
                    text=f"Segment: {segment_id}. Persona: Tech-savvy millennial. JTBD: Start investing with small amounts. Pain: Overwhelmed by complexity. Objections: 'Is it safe?', 'Do I need to know everything?' Preferred tone: Friendly, educational.",
                    metadata={"segment_id": segment_id}
                )
            ]
        else:
            stub_chunks = [
                Chunk(
                    chunk_id="segment_default_001",
                    doc_name="Segments",
                    doc_type="segment",
                    section="default",
                    page=None,
                    text="Default segment: General audience. Focus on accessibility and education. Avoid jargon.",
                    metadata={}
                )
            ]
        
        return stub_chunks[:top_k]
    
    def retrieve_all(
        self,
        query: str,
        product_scope: str,
        segment_id: Optional[str] = None,
        top_k_per_source: int = 3
    ) -> Dict[str, List[Chunk]]:
        """
        Retrieve chunks from all sources.
        
        Returns:
            Dict with keys: 'brand', 'product', 'segment'
        """
        return {
            "brand": self.retrieve_brand_chunks(query, top_k=top_k_per_source),
            "product": self.retrieve_product_info(product_scope, top_k=top_k_per_source),
            "segment": self.retrieve_segment_info(segment_id, top_k=top_k_per_source)
        }
