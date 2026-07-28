from google import genai

client = genai.Client(
    vertexai=True,
    project="hack-team-promptops",
    location="us-central1",      # e.g. us-central1
)

# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "gemini-2.5-flash-lite"