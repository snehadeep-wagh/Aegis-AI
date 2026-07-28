import mimetypes
from google.genai import types


def load_documents(document_paths: dict[str, str]) -> dict[str, types.Part]:
    """
    Convert document file paths into Gemini Parts.

    Args:
        document_paths:
            {
                "aadhaar": ".../aadhaar.jpg",
                "pan": ".../pan.png",
                "passport": ".../passport.pdf"
            }

    Returns:
        {
            "aadhaar": Part(...),
            "pan": Part(...),
            "passport": Part(...)
        }
    """

    documents = {}

    for document_name, path in document_paths.items():

        mime_type, _ = mimetypes.guess_type(path)

        if mime_type is None:
            mime_type = "application/octet-stream"

        with open(path, "rb") as f:
            documents[document_name] = types.Part.from_bytes(
                data=f.read(),
                mime_type=mime_type,
            )

    return documents