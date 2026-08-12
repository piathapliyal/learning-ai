import asyncio

from services.gemini_service import generate_embedding


async def main():
    text = "JavaScript promises handle asynchronous operations."

    embedding = await generate_embedding(text)

    print("Embedding dimension:", len(embedding))
    print("First 5 values:", embedding[:5])


asyncio.run(main())