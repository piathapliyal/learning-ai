from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from services.pdf_service import (
    extract_text_from_pdf,
    extract_text_from_txt,
    extract_text_from_docx,
)

from services.gemini_service import generate_learning_artifacts
from services.document_ingestion_service import ingest_document
from services.rag_service import generate_rag_answer

from database import SessionLocal
from models import Document

import json
import csv
import io


app = FastAPI()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Models
# ============================================================

class QuestionRequest(BaseModel):
    question: str
    session_id: int = 1


# ============================================================
# Document Upload
# ============================================================

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()

    # Extract text based on file type
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(contents)
        source_type = "pdf"

    elif file.content_type == "text/plain":
        text = extract_text_from_txt(contents)
        source_type = "txt"

    elif (
        file.content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        text = extract_text_from_docx(contents)
        source_type = "docx"

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the document",
        )

    # Generate learning artifacts
    artifacts = await generate_learning_artifacts(text)

    db = SessionLocal()

    try:
        # Create document, chunks, and embeddings
        document = await ingest_document(
            db=db,
            filename=file.filename,
            source_type=source_type,
            text=text,
        )

        # Save generated learning artifacts
        document.artifacts_json = artifacts.model_dump_json()

        db.commit()
        db.refresh(document)

        return {
            "document_id": document.id,
            "filename": file.filename,
            "source_type": source_type,
            "artifacts": artifacts,
        }

    finally:
        db.close()


# ============================================================
# Semantic RAG Question Answering
# ============================================================

@app.post("/documents/{document_id}/ask")
async def ask_document(
    document_id: int,
    request: QuestionRequest,
):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        answer = await generate_rag_answer(
            db=db,
            question=request.question,
            document_id=document_id,
            session_id=request.session_id,
             )

        return {
            "document_id": document_id,
            "question": request.question,
            "answer": answer["answer"],
            "sources": answer["sources"],
        }

    finally:
        db.close()


# ============================================================
# Get Document Learning Artifacts
# ============================================================

@app.get("/documents/{document_id}/artifacts")
async def get_document_artifacts(document_id: int):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        artifacts = json.loads(document.artifacts_json)

        return {
            "document_id": document.id,
            "filename": document.filename,
            "artifacts": artifacts,
        }

    finally:
        db.close()


# ============================================================
# Get Topic
# ============================================================

@app.get("/topics/{topic_name}")
async def get_topic(topic_name: str):
    db = SessionLocal()

    try:
        documents = db.query(Document).all()

        results = []

        for document in documents:
            artifacts = json.loads(document.artifacts_json)

            for topic in artifacts.get("topics", []):
                if topic["name"].lower() == topic_name.lower():
                    results.append(
                        {
                            "document_id": document.id,
                            "filename": document.filename,
                            "topic": topic,
                        }
                    )

        return {
            "topic": topic_name,
            "results": results,
        }

    finally:
        db.close()


# ============================================================
# Export Flashcards as CSV
# ============================================================

@app.get("/documents/{document_id}/flashcards/csv")
async def export_flashcards_csv(document_id: int):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        artifacts = json.loads(document.artifacts_json)

        flashcards = artifacts.get("flashcards", [])

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow(["Question", "Answer"])

        for flashcard in flashcards:
            writer.writerow(
                [
                    flashcard["question"],
                    flashcard["answer"],
                ]
            )

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{document.filename}_flashcards.csv"'
                )
            },
        )

    finally:
        db.close()


# ============================================================
# Concept Graph
# ============================================================

@app.get("/documents/{document_id}/concept-graph")
async def get_concept_graph(document_id: int):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        artifacts = json.loads(document.artifacts_json)

        concepts = artifacts.get("concepts", [])

        nodes = []
        edges = []

        for concept in concepts:
            nodes.append(
                {
                    "id": concept["name"],
                    "label": concept["name"],
                    "description": concept["description"],
                }
            )

        for i in range(len(concepts) - 1):
            edges.append(
                {
                    "source": concepts[i]["name"],
                    "target": concepts[i + 1]["name"],
                }
            )

        return {
            "document_id": document.id,
            "filename": document.filename,
            "nodes": nodes,
            "edges": edges,
        }

    finally:
        db.close()