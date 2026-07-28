import vertexai
from google.cloud import aiplatform

PROJECT_ID = "hack-team-promptops"
LOCATION = "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)

print("Connected to Vertex AI successfully!")