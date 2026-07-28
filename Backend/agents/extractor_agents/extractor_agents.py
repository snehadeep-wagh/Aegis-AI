from google.genai import types

from config.gemini_client import client, MODEL_NAME
from models.extractor_model import ExtractResponse
from google.genai.types import Part


class ExtractorAgent:

    def __init__(self):
        with open("prompts/extractor.txt", "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def extract(self, documents: dict[str, object]) -> dict[str, ExtractResponse]:
        """
        Extract data from multiple documents.

        Args:
            documents:
                {
                    "aadhaar": <image>,
                    "pan": <image>,
                    ...
                }

        Returns:
            {
                "aadhaar": ExtractResponse(...),
                "pan": ExtractResponse(...),
                ...
            }
        """

        results = {}

        for document_name, document in documents.items():

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    self.prompt,
                    Part.from_uri(
    file_uri=document,
    mime_type="image/png"
),
                ],
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=ExtractResponse,
                ),
            )

            results[document_name] = response.parsed

        return results