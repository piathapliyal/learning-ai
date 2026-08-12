import asyncio

from database import SessionLocal
from services.search_service import semantic_search


async def main():
    db = SessionLocal()

    try:
        results = await semantic_search(
            db,
            "How does JavaScript handle asynchronous tasks?",
            limit=5,
        )

        for result in results:
            print(f"\nChunk ID: {result.id}")
            print(f"Content: {result.content}")

    finally:
        db.close()


asyncio.run(main())