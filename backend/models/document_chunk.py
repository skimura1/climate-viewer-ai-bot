"""
SQLAlchemy model for document chunks with embeddings.

This model stores text chunks from climate literature documents along with their
embeddings and metadata for RAG (Retrieval Augmented Generation) applications.
"""

from sqlalchemy import ARRAY, JSON, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

from pgvector.sqlalchemy import Vector

Base = declarative_base()


class DocumentChunk(Base):
    """
    SQLAlchemy model for storing document chunks with embeddings.

    This model stores text chunks from documents along with their embeddings
    and metadata for semantic search and RAG applications.

    Attributes:
        id: Primary key
        chunk_id: Unique identifier for the chunk
        chunk_index: Index of chunk within the source document
        text: The actual text content of the chunk
        embedding: Vector embedding (1536 dimensions for OpenAI ada-002/text-embedding-3-small)
        filename: Original document filename
        source_file: Path to the source file
        relevant: Whether the chunk is relevant (1=True, 0=False)
        confidence: Confidence level (HIGH, MEDIUM, LOW)
        relevant_layers: Array of climate layer names
        reasoning: Explanation of relevance assessment
        key_findings: JSON object with key findings
        locations: Array of Hawaiian locations mentioned
        slr_projections: Array of sea level rise projections
        measurements: Array of measurements/quantitative data
        timeframes: Array of time periods mentioned
    """

    __tablename__ = "document_chunks"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Chunk identification
    chunk_id = Column(String(255), unique=True, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)

    # Content
    text = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension

    # Document metadata
    filename = Column(String(500), nullable=False, index=True)
    source_file = Column(String(500))

    # Relevance metadata
    relevant = Column(Integer, default=1)  # Using Integer for boolean (1=True, 0=False)
    confidence = Column(String(50), index=True)  # HIGH, MEDIUM, LOW
    relevant_layers = Column(ARRAY(String), index=True)  # Array of layer names
    reasoning = Column(Text)
    key_findings = Column(JSON)

    # Location and measurement data
    locations = Column(ARRAY(String))
    slr_projections = Column(ARRAY(String))
    measurements = Column(ARRAY(String))
    timeframes = Column(ARRAY(String))

    def __repr__(self):
        """String representation of the DocumentChunk."""
        return (
            f"<DocumentChunk(id={self.id}, chunk_id='{self.chunk_id}', "
            f"filename='{self.filename}')>"
        )

    def to_dict(self):
        """
        Convert the chunk to a dictionary.

        Returns:
            Dictionary representation of the chunk with all fields
        """
        return {
            "id": self.id,
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "filename": self.filename,
            "source_file": self.source_file,
            "relevant": bool(self.relevant),
            "confidence": self.confidence,
            "relevant_layers": self.relevant_layers,
            "reasoning": self.reasoning,
            "key_findings": self.key_findings,
            "locations": self.locations,
            "slr_projections": self.slr_projections,
            "measurements": self.measurements,
            "timeframes": self.timeframes,
        }