from sqlalchemy.orm import Session

from models import DocumentChunk
from services.gemini_service import generate_embedding


async def create_chunk_embedding(
    db: Session,
    chunk: DocumentChunk
):
    embedding = await generate_embedding(chunk.content)

    chunk.embedding = embedding

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk