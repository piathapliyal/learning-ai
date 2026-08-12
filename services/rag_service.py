from sqlalchemy import select
from sqlalchemy.orm import Session

from models import DocumentChunk
from services.gemini_service import generate_embedding

from google import genai
import os


async def retrieve_chunks(
    db: Session,
    question: str,
    document_id: int,
    limit: int = 5,
):
    question_embedding = await generate_embedding(question)

    distance = DocumentChunk.embedding.cosine_distance(
        question_embedding
    )

    statement = (
        select(DocumentChunk)
        .where(
            DocumentChunk.embedding.is_not(None),
            DocumentChunk.document_id == document_id,
        )
        .order_by(distance)
        .limit(limit)
    )

    result = db.execute(statement)

    return result.scalars().all()


async def generate_rag_answer(
    db: Session,
    question: str,
    document_id: int,
):
    chunks = await retrieve_chunks(
        db=db,
        question=question,
        document_id=document_id,
    )

    if not chunks:
        return "I couldn't find relevant information in the uploaded material."

    context = "\n\n".join(
        f"[Source {index + 1}]\n{chunk.content}"
        for index, chunk in enumerate(chunks)
    )

    prompt = f"""
You are a learning assistant.

Answer the user's question using ONLY the provided learning material.

If the answer cannot be found in the material, say that the information
is not available in the provided material.

Learning material:

{context}

User question:
{question}

Give a clear and concise answer.
"""

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text