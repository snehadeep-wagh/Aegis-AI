from config.gemini_client import client, MODEL_NAME
from google.genai.types import Part


class ClassifierAgent:

    def __init__(self):
        with open("prompts/classifier.txt", "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def classify(self, documents: dict[str, object]) -> dict[str, str]:
        """
        Classify multiple documents.

        Args:
            documents:
                {
                    "aadhaar": <image>,
                    "pan": <image>,
                    ...
                }

        Returns:
            {
                "aadhaar": "Aadhaar",
                "pan": "PAN",
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
            )

            document_type = response.text.strip()

            # print(f"\nClassifier Agent - {document_name}:")
            # print(document_type)

            results[document_name] = document_type

        return results