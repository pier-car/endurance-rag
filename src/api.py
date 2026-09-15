from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="EnduranceRAG")

class Query(BaseModel):
    domanda: str

@app.post("/ask")
def ask(q: Query):
    return {"risposta": run_agent(q.domanda, verbose=False)}