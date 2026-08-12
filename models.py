from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from datetime import datetime

from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    artifacts_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    content = Column(Text, nullable=False)

    chunk_index = Column(Integer, nullable=False)

    embedding = Column(Vector(768), nullable=True)