from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

from backend.agents.router_agent import route_query
from backend.agents.rag_agent import run_rag_agent
from backend.agents.data_agent import run_data_agent, load_csv, get_loaded_files
from backend.agents.research_agent import run_research_agent
from backend.rag.ingest import ingest_pdf

app = FastAPI(title="AI Enterprise Copilot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    filename: str = None  # optional: target a specific CSV

class ChatResponse(BaseModel):
    answer: str
    route: str
    sources: list[str] = []

@app.get("/")
def health():
    return {"status": "ok", "message": "AI Copilot is running"}

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    content = await file.read()
    chunks = ingest_pdf(content, file.filename)
    return {"message": f"Ingested {chunks} chunks from '{file.filename}'"}

@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    content = await file.read()
    name = load_csv(content, file.filename)
    return {"message": f"Loaded CSV '{name}'", "filename": name}

@app.get("/files")
def list_files():
    return {"csv_files": get_loaded_files()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    route = route_query(question)

    if route == "RAG":
        result = run_rag_agent(question)
        return ChatResponse(answer=result["answer"], route=route, sources=result.get("sources", []))

    elif route == "DATA":
        result = run_data_agent(question, filename=request.filename)
        return ChatResponse(answer=result["answer"], route=route)

    else:  # RESEARCH
        result = run_research_agent(question)
        return ChatResponse(answer=result["answer"], route=route, sources=result.get("sources", []))
