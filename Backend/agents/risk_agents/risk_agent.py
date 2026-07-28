from google.genai import types

from config.gemini_client import client, MODEL_NAME
from models.risk_model import RiskResponse
from google.genai.types import Part

class RiskAgent:

    def __init__(self):
        with open("prompts/risk.txt", "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def evaluate(self, documents: dict[str, object]) -> dict[str, RiskResponse]:
        """
        Evaluate authenticity for multiple documents.

        Args:
            documents:
                {
                    "aadhaar": <image>,
                    "pan": <image>,
                    ...
                }

        Returns:
            {
                "aadhaar": RiskResponse(...),
                "pan": RiskResponse(...),
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
                    response_schema=RiskResponse,
                ),
            )

            # print(f"\nRisk Agent - {document_name}:\n")
            # print(response.text)

            results[document_name] = response.parsed

        return results