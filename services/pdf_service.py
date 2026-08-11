import io
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(contents: bytes) -> str:
    reader = PdfReader(io.BytesIO(contents))
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_text_from_txt(contents: bytes) -> str:
    return contents.decode("utf-8")


def extract_text_from_docx(contents: bytes) -> str:
    from io import BytesIO

    document = Document(BytesIO(contents))

    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )