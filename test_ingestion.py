import asyncio

from database import SessionLocal
from services.document_ingestion_service import ingest_document


async def main():
    db = SessionLocal()

    try:
        text = """
        JavaScript promises represent the eventual completion or failure
        of an asynchronous operation. A promise can be pending, fulfilled,
        or rejected.

        Promises are useful when working with asynchronous operations
        because they allow developers to handle results and errors in a
        structured way.
        """

        document = await ingest_document(
            db=db,
            filename="javascript-promises.txt",
            source_type="test",
            text=text,
        )

        print("Document ID:", document.id)
        print("Document:", document.filename)

    finally:
        db.close()


asyncio.run(main())