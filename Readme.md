# Learning AI — Multi-Source Learning Content Ingestion

## Overview

Learning AI is a FastAPI-based application that converts learning content into structured educational artifacts using Google Gemini.

The application accepts supported document formats, extracts their text, processes the content with Gemini, validates the generated structure using Pydantic, and stores the results in SQLite using SQLAlchemy.

The generated artifacts include:

- Summary
- Flashcards
- Key concepts
- Topics and subtopics
- Concept graph / learning path

---

## Features

### Multi-Source Content Ingestion

Currently supported:

- PDF
- TXT
- DOCX
- Text-based transcripts through TXT ingestion

Direct video/audio transcription is **not implemented** in the current MVP.

### AI-Powered Learning Artifacts

For each uploaded document, Gemini generates:

- A concise summary
- Question/answer flashcards
- Important concepts with descriptions
- Topics and subtopics

### Persistent Storage

Generated artifacts are stored in SQLite using SQLAlchemy.

Each uploaded document stores:

- Document ID
- Filename
- Source type
- Generated artifacts
- Creation timestamp

### Topic-Based Retrieval

Stored learning content can be retrieved using:


GET /topics/{topic_name}

The endpoint retrieves matching topics and their subtopics from stored documents.

CSV Flashcard Export

Flashcards can be exported as a CSV file:

GET /documents/{document_id}/flashcards/csv

This makes the generated flashcards usable in spreadsheet applications and other learning workflows.

Concept Graph

The application exposes:

GET /documents/{document_id}/concept-graph

The endpoint returns concept nodes and edges representing a simple sequential learning path between extracted concepts.

Architecture
Uploaded Content
       |
   +---+---+---+
   |   |   |
  PDF TXT DOCX
   |   |   |
   +---+---+
       |
       v
Text Extraction
       |
       v
Gemini AI Service
       |
       v
Pydantic Validation
       |
       v
Learning Artifacts
       |
   +---+---+---+
   |   |   |
Summary Flashcards Concepts
              |
              v
        Topics/Subtopics
              |
              v
       SQLite Database
              |
       +------+------+ 
       |      |      |
       v      v      v
    Topic   CSV   Concept
 Retrieval Export   Graph


Technology Stack
Python
FastAPI
Google Gemini API
Pydantic
SQLAlchemy
SQLite
python-docx
PyPDF
Uvicorn



Project Structure
backend/
│
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── .env
├── .gitignore
│
└── services/
    ├── gemini_service.py
    └── pdf_service.py


API Endpoints
Method	Endpoint	Description
POST	/documents/upload	Upload a PDF, TXT, or DOCX document and generate learning artifacts
GET	/topics/{topic_name}	Retrieve a matching stored topic and its subtopics
GET	/documents/{document_id}/flashcards/csv	Export generated flashcards as CSV
GET	/documents/{document_id}/concept-graph	Retrieve concept nodes and relationships

Example Workflow
Upload a PDF, TXT, or DOCX file.
Extract the text from the document.
Send the extracted content to Gemini.
Generate summary, flashcards, concepts, topics, and subtopics.
Validate the generated response using Pydantic.
Store the generated artifacts in SQLite.
Retrieve learning content by topic.
Export flashcards as CSV.
Retrieve the concept graph.


Setup
1. Create a virtual environment
python -m venv venv
2. Activate the virtual environment
.\venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure the Gemini API key

Create a .env file:

GEMINI_API_KEY=your_api_key

Do not commit the .env file to GitHub.

5. Run the application
uvicorn main:app --reload

The application runs at:

http://127.0.0.1:8000

FastAPI Swagger documentation:

http://127.0.0.1:8000/docs
Demo Flow

A sample learning document can be used to demonstrate the complete pipeline:

Document Upload
      |
      v
Text Extraction
      |
      v
Gemini Processing
      |
      v
+---------------------------+
| Summary                   |
| Flashcards                |
| Concepts                  |
| Topics & Subtopics        |
+---------------------------+
      |
      v
Pydantic Validation
      |
      v
SQLite Storage
      |
      +------------+------------+
      |            |            |
      v            v            v
   Topic          CSV        Concept
  Retrieval      Export       Graph


Current Limitations
Direct video/audio transcription is not implemented.
Topic retrieval currently uses exact topic-name matching.
The concept graph currently uses a simple sequential learning path rather than fully semantic relationships.
Generated artifacts are stored as JSON within the document record rather than as fully normalized relational tables.
Large documents would benefit from chunking and hierarchical processing.
AI failure and retry handling can be improved.
Future Improvements
Multimedia Ingestion
Add direct video/audio ingestion using speech-to-text.
Support SRT/VTT transcript formats.
Add OCR support for scanned PDFs.
Retrieval
Replace exact topic-name matching with semantic topic search.
Support semantic retrieval across concepts, topics, and flashcards.
Concept Graph
Replace sequential concept connections with true semantic relationships.
Support relationship types such as:
prerequisite
related_to
part_of
depends_on
Use stable technical concept IDs such as concept_1, concept_2, etc.
Keep the human-readable concept name in a separate label field.

Example:

{
  "id": "concept_1",
  "label": "Supervised Learning",
  "description": "Learning using labeled data."
}
Database
Normalize concepts, topics, flashcards, and relationships into dedicated database tables.
Add indexes for efficient retrieval at larger scale.
Large Documents
Add document chunking.
Process large documents hierarchically.
Combine chunk-level results into a final learning structure.
Reliability
Add Gemini retry and timeout handling.
Improve handling of malformed AI responses.
Improve validation and error reporting.
Application Features
Add frontend visualization for the concept graph.
Add authentication.
Support user-specific document collections.