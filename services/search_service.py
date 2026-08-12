from sqlalchemy import select
from sqlalchemy.orm import Session

from models import DocumentChunk
from services.gemini_service import generate_embedding


async def semantic_search(
    db: Session,
    query: str,
    limit: int = 5,
):
    query_embedding = await generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )

    result = db.execute(statement)

    return result.scalars().all()