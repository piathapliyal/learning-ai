from sqlalchemy.orm import Session

from models import Document, DocumentChunk
from services.chunking_service import chunk_text
from services.embedding_service import create_chunk_embedding


async def ingest_document(
    db: Session,
    filename: str,
    source_type: str,
    text: str,
):
    # 1. Create the document record
    document = Document(
        filename=filename,
        source_type=source_type,
        artifacts_json="{}",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # 2. Split extracted text into chunks
    chunks = chunk_text(text)

    # 3. Create and embed each chunk
    for index, content in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document.id,
            content=content,
            chunk_index=index,
        )

        db.add(chunk)
        db.commit()
        db.refresh(chunk)

        await create_chunk_embedding(db, chunk)

    return document