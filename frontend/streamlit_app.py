import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Enterprise Copilot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Enterprise Copilot")
st.caption("Powered by Groq (LLaMA 3) · Free · Fast · No GPU needed")

# ── Sidebar: File Uploads ──────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Upload Files")

    st.subheader("📄 PDF Documents")
    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if pdf_file and st.button("Ingest PDF"):
        with st.spinner("Ingesting..."):
            res = requests.post(
                f"{BACKEND_URL}/upload/pdf",
                files={"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")},
            )
        if res.ok:
            st.success(res.json()["message"])
        else:
            st.error("Failed to ingest PDF")

    st.divider()

    st.subheader("📊 CSV / Data Files")
    csv_file = st.file_uploader("Upload a CSV", type=["csv"])
    if csv_file and st.button("Load CSV"):
        with st.spinner("Loading..."):
            res = requests.post(
                f"{BACKEND_URL}/upload/csv",
                files={"file": (csv_file.name, csv_file.getvalue(), "text/csv")},
            )
        if res.ok:
            st.success(res.json()["message"])
            st.session_state["active_csv"] = res.json()["filename"]
        else:
            st.error("Failed to load CSV")

    st.divider()
    st.caption("**Route legend:**\n- 🗂 RAG → PDF docs\n- 📊 DATA → CSV files\n- 🌐 RESEARCH → Web search")

# ── Chat Interface ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "route" in msg:
            route_icons = {"RAG": "🗂", "DATA": "📊", "RESEARCH": "🌐"}
            icon = route_icons.get(msg["route"], "🤖")
            st.caption(f"{icon} Answered via: **{msg['route']}**")
        if msg.get("sources"):
            st.caption(f"Sources: {', '.join(msg['sources'])}")

# Chat input
if prompt := st.chat_input("Ask anything — about your docs, data, or the web..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {"question": prompt}
            if "active_csv" in st.session_state:
                payload["filename"] = st.session_state["active_csv"]

            try:
                res = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
                data = res.json()
                answer = data["answer"]
                route = data.get("route", "")
                sources = data.get("sources", [])

                st.markdown(answer)
                route_icons = {"RAG": "🗂", "DATA": "📊", "RESEARCH": "🌐"}
                icon = route_icons.get(route, "🤖")
                st.caption(f"{icon} Answered via: **{route}**")
                if sources:
                    st.caption(f"Sources: {', '.join(sources)}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "route": route,
                    "sources": sources,
                })

            except Exception as e:
                st.error(f"Error: {e}")
