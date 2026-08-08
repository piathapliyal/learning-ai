from fastapi import FastAPI, UploadFile, File
from services.pdf_service import extract_text_from_pdf



app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    return {
        "filename": file.filename,
        "text": text
    }