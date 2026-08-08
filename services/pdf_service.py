import io
from pypdf import PdfReader


def extract_text_from_pdf(contents: bytes) -> str:
    reader = PdfReader(io.BytesIO(contents))
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text