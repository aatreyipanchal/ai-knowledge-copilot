# 🤖 AI Enterprise Copilot

A **multi-agent AI assistant** built with LLaMA 3 on Groq (free + fast), LangChain, ChromaDB, FastAPI, and Streamlit. No GPU required.

## ✨ Features

| Agent | What it does | Model used |
|---|---|---|
| 🗂 RAG Agent | Answers questions from your uploaded PDFs | llama-3.3-70b |
| 📊 Data Agent | Analyzes your CSV files | llama-3.3-70b |
| 🌐 Research Agent | Searches the web via DuckDuckGo | llama-3.3-70b |
| 🔀 Router Agent | Routes your query to the right agent | llama-3.1-8b-instant |

## 🗂 Project Structure

```
ai-knowledge-copilot/
├── backend/
│   ├── app.py                   ← FastAPI entry point
│   ├── agents/
│   │   ├── router_agent.py      ← Routes query to correct agent
│   │   ├── rag_agent.py         ← PDF Q&A with ChromaDB
│   │   ├── data_agent.py        ← CSV analysis with Pandas + LLM
│   │   └── research_agent.py   ← Web search + summarization
│   ├── rag/
│   │   └── ingest.py            ← PDF loading + chunking
│   └── database/
│       └── vector_store.py      ← ChromaDB + embeddings setup
├── frontend/
│   └── streamlit_app.py         ← Chat UI
├── deployment/
│   └── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-knowledge-copilot.git
cd ai-knowledge-copilot

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add API Key

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
# Get free key at: https://console.groq.com
```

### 3. Run Backend

```bash
uvicorn backend.app:app --reload --port 8000
```

### 4. Run Frontend (new terminal)

```bash
streamlit run frontend/streamlit_app.py
```

Open http://localhost:8501 in your browser.

## ☁️ Free Deployment

### Backend → Render.com
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port 8000`
6. Add environment variable: `GROQ_API_KEY=your_key`

### Frontend → Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repo
3. Set main file: `frontend/streamlit_app.py`
4. Add secret: `BACKEND_URL=https://your-render-app.onrender.com`

## 🔑 Get Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create API key
4. Add to `.env` file

## 📝 Resume Description

> Developed a multi-agent AI enterprise assistant combining RAG pipelines, data analysis agents, and web research agents using LLaMA 3 on Groq for zero-cost, low-latency inference. Built a FastAPI backend with LangChain orchestration, ChromaDB vector store with CPU-based sentence-transformers embeddings, and deployed a full-stack AI system on Render + Streamlit Cloud supporting document intelligence and data-driven insights.

## 🛠️ Tech Stack

- **LLM**: LLaMA 3.3 70B + 3.1 8B via Groq API (free tier)
- **Embeddings**: `all-MiniLM-L6-v2` via sentence-transformers (CPU)
- **Vector DB**: ChromaDB (local) 
- **Web Search**: DuckDuckGo (no API key needed)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Deployment**: Render.com + Streamlit Cloud (both free)
