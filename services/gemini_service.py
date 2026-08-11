import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


class Flashcard(BaseModel):
    question: str
    answer: str


class Concept(BaseModel):
    name: str
    description: str

class Topic(BaseModel):
    name: str
    subtopics: list[str]


class LearningArtifacts(BaseModel):
    summary: str
    flashcards: list[Flashcard]
    concepts: list[Concept]
    topics: list[Topic]




load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

async def test_gemini():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one sentence."
        
    )
    return response.text


async def generate_learning_artifacts(text: str):
    prompt = f"""
    Analyze the following learning material and create useful study artifacts.

    Learning material:
    {text}

    Return:
    - A concise summary
    - Main topics and their subtopics
    - Important concepts with descriptions
    - Useful flashcards with questions and answers
    """

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_schema": LearningArtifacts,
    }
    )

    return LearningArtifacts.model_validate_json(response.text)



