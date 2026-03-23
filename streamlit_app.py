import streamlit as st
import os
import base64
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Add the current directory to sys.path to ensure backend imports work
import sys
sys.path.append(os.path.abspath(os.curdir))

from backend.agents.router_agent import route_query
from backend.agents.rag_agent import run_rag_agent
from backend.agents.data_agent import run_data_agent, load_csv, get_loaded_files
from backend.agents.research_agent import run_research_agent
from backend.agents.vision_agent import run_vision_agent
from backend.rag.ingest import ingest_pdf
from backend.database.database import init_db, SessionLocal, Conversation

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Knowledge Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stSidebar {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    /* Ensure all sidebar text is visible */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stHeader, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown span {
        color: #ffffff !important;
    }
    /* Universal text visibility for main area if needed */
    .stMarkdown, .stSubheader, .stTitle {
        color: #e6edf3;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #238636;
        color: white;
    }
    .stHeader {
        color: #58a6ff;
    }
    .source-tag {
        background-color: #21262d;
        color: #8b949e;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    # Load history from DB
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == st.session_state.session_id).order_by(Conversation.timestamp).all()
    db.close()
    
    st.session_state.messages = []
    for msg in history:
        extra_info = json.loads(msg.extra_info) if msg.extra_info else {}
        st.session_state.messages.append({
            "role": msg.role,
            "content": msg.content,
            "route": extra_info.get("route"),
            "sources": extra_info.get("sources", []),
            "charts": extra_info.get("charts", [])
        })

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- Sidebar: File Management ---
with st.sidebar:
    st.title("📂 Knowledge Base")
    st.markdown("---")
    
    st.subheader("Upload Files")
    
    # PDF Upload
    pdf_file = st.file_uploader("Upload PDF (Documents)", type=["pdf"], key="pdf_uploader")
    if pdf_file:
        if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
            with st.spinner(f"Ingesting {pdf_file.name}..."):
                content = pdf_file.read()
                chunks = ingest_pdf(content, pdf_file.name)
                st.success(f"Ingested {chunks} chunks from PDF.")
                st.session_state.last_pdf = pdf_file.name
                st.session_state.selected_file = pdf_file.name

    # CSV Upload
    csv_file = st.file_uploader("Upload CSV (Data)", type=["csv"], key="csv_uploader")
    if csv_file:
        if "last_csv" not in st.session_state or st.session_state.last_csv != csv_file.name:
            with st.spinner(f"Loading {csv_file.name}..."):
                content = csv_file.read()
                name = load_csv(content, csv_file.name)
                st.success(f"Loaded CSV '{name}'.")
                st.session_state.last_csv = csv_file.name
                st.session_state.selected_file = csv_file.name

    # Image Upload
    img_file = st.file_uploader("Upload Image (Vision)", type=["png", "jpg", "jpeg"], key="img_uploader")
    if img_file:
        if "last_img" not in st.session_state or st.session_state.last_img != img_file.name:
            with st.spinner(f"Uploading {img_file.name}..."):
                img_path = os.path.join(UPLOAD_DIR, img_file.name)
                with open(img_path, "wb") as f:
                    f.write(img_file.read())
                st.success(f"Uploaded image '{img_file.name}'.")
                st.session_state.last_img = img_file.name
                st.session_state.selected_file = img_file.name

    st.markdown("---")
    st.subheader("Context")
    
    all_files = get_loaded_files() # This only gets CSVs based on current implementation
    # Let's show the "active" file
    if st.session_state.selected_file:
        st.info(f"Active Context: **{st.session_state.selected_file}**")
        if st.button("Clear Context"):
            st.session_state.selected_file = None
            st.rerun()
    else:
        st.warning("No active file context selected.")

# --- Main UI ---
st.title("🤖 AI Knowledge Copilot")
st.markdown("Your intelligent partner for Documents, Data, Vision, and Research.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
             st.markdown("---")
             st.markdown("**Sources:**")
             cols = st.columns(len(message["sources"]))
             for i, source in enumerate(message["sources"]):
                 st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
        
        if message.get("charts"):
            for chart_base64 in message["charts"]:
                st.image(base64.b64decode(chart_base64))

# Chat Input
if prompt := st.chat_input("Ask me anything about your files..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Route Query
            route = route_query(prompt, filename=st.session_state.selected_file)
            
            # 2. Run Agent
            answer = ""
            sources = []
            charts = []
            
            if route == "RAG":
                rag_file = st.session_state.selected_file if st.session_state.selected_file and st.session_state.selected_file.lower().endswith(".pdf") else None
                result = run_rag_agent(prompt, session_id=st.session_state.session_id, filename=rag_file)
                answer = result["answer"]
                sources = result.get("sources", [])
            elif route == "DATA":
                data_file = st.session_state.selected_file if st.session_state.selected_file and st.session_state.selected_file.lower().endswith(".csv") else None
                result = run_data_agent(prompt, session_id=st.session_state.session_id, filename=data_file)
                answer = result["answer"]
                charts = result.get("charts", [])
            elif route == "IMAGE":
                img_name = st.session_state.selected_file
                img_bytes = None
                if img_name:
                    img_path = os.path.join(UPLOAD_DIR, img_name)
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            img_bytes = f.read()
                
                if img_bytes:
                    result = run_vision_agent(img_bytes, prompt, session_id=st.session_state.session_id)
                    answer = result["answer"]
                else:
                    answer = "No image found to analyze. Please upload an image first."
            else:
                result = run_research_agent(prompt, session_id=st.session_state.session_id)
                answer = result["answer"]
                sources = result.get("sources", [])

            # 3. Render Response
            st.markdown(answer)
            if sources:
                st.markdown("---")
                st.markdown("**Sources:**")
                for source in sources:
                    st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
            
            if charts:
                for chart_base64 in charts:
                    st.image(base64.b64decode(chart_base64))

            # 4. Save Assistant Message to DB
            metadata = {
                "route": route,
                "sources": sources,
                "charts": charts if route == "DATA" else []
            }
            from backend.agents.base_agent import BaseAgent
            BaseAgent().save_message(st.session_state.session_id, "assistant", answer, metadata=metadata)
            
            # 5. Update Session State
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "route": route, 
                "sources": sources, 
                "charts": charts
            })

    if st.button("🗑️ Clear Chat History"):
        # We don't delete from DB in this simple version, just session state
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4()) # New session
        st.rerun()
