from fastapi import FastAPI, UploadFile, File
from services.pdf_service import (
    extract_text_from_pdf,
    extract_text_from_txt,
    extract_text_from_docx
)
from services.gemini_service import generate_learning_artifacts
from database import engine, Base, SessionLocal
import models
from models import Document
import json
import csv
import io

from fastapi.responses import StreamingResponse


Base.metadata.create_all(bind=engine)




app = FastAPI()

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()

    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(contents)
        source_type = "pdf"

    elif file.content_type == "text/plain":
        text = extract_text_from_txt(contents)
        source_type = "txt"

    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(contents)
        source_type = "docx"

    else:
        return {"error": "Unsupported file type"}

    artifacts = await generate_learning_artifacts(text)

    db = SessionLocal()

    document = Document(
        filename=file.filename,
        source_type=source_type,
        artifacts_json=artifacts.model_dump_json()
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    db.close()

    return {
        "document_id": document.id,
        "filename": file.filename,
        "source_type": source_type,
        "artifacts": artifacts
    }



@app.get("/topics/{topic_name}")
async def get_topic(topic_name: str):
    db = SessionLocal()

    documents = db.query(Document).all()

    results = []

    for document in documents:
        artifacts = json.loads(document.artifacts_json)


        for topic in artifacts.get("topics", []):
            if topic["name"].lower() == topic_name.lower():
                results.append({
                    "document_id": document.id,
                    "filename": document.filename,
                    "topic": topic
                })

    db.close()

    return {
        "topic": topic_name,
        "results": results
    }



@app.get("/documents/{document_id}/flashcards/csv")
async def export_flashcards_csv(document_id: int):
    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    db.close()

    if not document:
        return {"error": "Document not found"}

    artifacts = json.loads(document.artifacts_json)

    flashcards = artifacts.get("flashcards", [])

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(["Question", "Answer"])

    for flashcard in flashcards:
        writer.writerow([
            flashcard["question"],
            flashcard["answer"]
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{document.filename}_flashcards.csv"'
            )
        }
    )



@app.get("/documents/{document_id}/concept-graph")
async def get_concept_graph(document_id: int):
    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    db.close()

    if not document:
        return {"error": "Document not found"}

    artifacts = json.loads(document.artifacts_json)

    concepts = artifacts.get("concepts", [])

    nodes = []
    edges = []

    for concept in concepts:
        nodes.append({
            "id": concept["name"],
            "label": concept["name"],
            "description": concept["description"]
        })

    for i in range(len(concepts) - 1):
        edges.append({
            "source": concepts[i]["name"],
            "target": concepts[i + 1]["name"]
        })

    return {
        "document_id": document.id,
        "filename": document.filename,
        "nodes": nodes,
        "edges": edges
    }