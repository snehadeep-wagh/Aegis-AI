from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

from agents.master_agents.master_agent import MasterAgent

app = FastAPI()

master = MasterAgent()


class VerifyRequest(BaseModel):
    documents: Dict[str, str]


@app.post("/verify")
async def verify(request: VerifyRequest):

    result = master.process(request.documents)

    return result