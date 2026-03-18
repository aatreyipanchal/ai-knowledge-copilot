from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
import os

load_dotenv()

from backend.agents.router_agent import route_query
from backend.agents.rag_agent import run_rag_agent
from backend.agents.data_agent import run_data_agent, load_csv, get_loaded_files
from backend.agents.research_agent import run_research_agent
from backend.agents.vision_agent import run_vision_agent
from backend.rag.ingest import ingest_pdf
from backend.database.database import init_db, SessionLocal, Conversation

init_db()

app = FastAPI(title="AI Knowledge Copilot", version="1.0.0")

_image_store: dict[str, bytes] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    filename: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    route: str
    sources: list[str] = []
    chart: Optional[str] = None   # ← was str, now Optional[str]

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

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG/JPG files allowed")
    content = await file.read()
    _image_store[file.filename] = content
    return {"message": f"Uploaded image '{file.filename}'", "filename": file.filename}

@app.get("/files")
def list_files():
    return {"csv_files": get_loaded_files()}

# --- List Files Endpoint ---

# --- Persistent Chat Endpoint ---

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default_session"
    filename: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    db = SessionLocal()
    
    # Route and run agents
    route = route_query(question)

    if route == "RAG":
        # Only filter by filename if it's a PDF
        rag_file = request.filename if request.filename and request.filename.lower().endswith(".pdf") else None
        result = run_rag_agent(question, session_id=request.session_id, filename=rag_file)
        answer = result["answer"]
        sources = result.get("sources", [])
        chart = None
    elif route == "DATA":
        # Only filter by filename if it's a CSV
        data_file = request.filename if request.filename and request.filename.lower().endswith(".csv") else None
        result = run_data_agent(question, session_id=request.session_id, filename=data_file)
        answer = result["answer"]
        chart = result.get("chart")
        sources = []
    elif route == "IMAGE":
        # Get the latest uploaded image if filename not provided
        img_name = request.filename
        if not img_name and _image_store:
            img_name = list(_image_store.keys())[-1]
        
        if img_name and img_name in _image_store:
            result = run_vision_agent(_image_store[img_name], question, session_id=request.session_id)
            answer = result["answer"]
        else:
            answer = "No image found to analyze. Please upload an image first."
            # Manual save since run_vision_agent wasn't called
            from backend.agents.base_agent import BaseAgent
            BaseAgent().save_message(request.session_id, "user", question)
        sources = []
        chart = None
    else:
        result = run_research_agent(question, session_id=request.session_id)
        answer = result["answer"]
        sources = result.get("sources", [])
        chart = None

    # Save assistant message with metadata
    metadata = {
        "route": route,
        "sources": sources,
        "chart": chart
    }
    
    # We use the BaseAgent's save_message instance if needed, or just do it here
    from backend.agents.base_agent import BaseAgent
    BaseAgent().save_message(request.session_id, "assistant", answer, metadata=metadata)

    db.close()
    return ChatResponse(answer=answer, route=route, sources=sources, chart=chart)

@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == session_id).order_by(Conversation.timestamp).all()
    db.close()
    return history