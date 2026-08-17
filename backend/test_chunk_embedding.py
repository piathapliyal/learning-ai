import asyncio

from database import SessionLocal
from models import Document, DocumentChunk
from services.embedding_service import create_chunk_embedding
from services.search_service import semantic_search


async def create_test_chunk(db, content, index):
    document = Document(
        filename=f"semantic-test-{index}.txt",
        source_type="test",
        artifacts_json="{}"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        content=content,
        chunk_index=0
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    await create_chunk_embedding(db, chunk)

    return chunk


async def main():
    db = SessionLocal()

    try:
        chunks = [
            "JavaScript promises handle asynchronous operations.",
            "Python decorators modify or extend the behavior of functions.",
            "PostgreSQL indexes improve the speed of database queries."
        ]

        for index, content in enumerate(chunks):
            chunk = await create_test_chunk(db, content, index)
            print(f"Created chunk {chunk.id}: {content}")

        print("\n--- Search 1 ---")

        results = await semantic_search(
            db,
            "How does JavaScript handle asynchronous tasks?",
            limit=3
        )

        for result in results:
            print(f"Chunk {result.id}: {result.content}")

        print("\n--- Search 2 ---")

        results = await semantic_search(
            db,
            "How can I make database queries faster?",
            limit=3
        )

        for result in results:
            print(f"Chunk {result.id}: {result.content}")

    finally:
        db.close()


asyncio.run(main())