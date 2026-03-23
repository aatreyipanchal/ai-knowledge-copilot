#  AI Knowledge Copilot: Multi-Agent Intelligence System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-knowledge-copilot.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An **Elite Multi-Agent AI System** that transforms how you interact with your data. Powered by LLaMA 3.3 (70B) on Groq for lightning-fast inference, this Copilot handles Documents, Structured Data, Vision, and Web Research in a unified, premium interface.

---

##  Key Capabilities

| Agent | Icon | Description | Core Technology |
| :--- | :---: | :--- | :--- |
| **Document Intelligence (RAG)** | 📜 | Semantic search and Q&A across multi-page PDFs. | LangChain + ChromaDB |
| **Statistical Analyst (DATA)** | 📊 | Deep CSV analysis, automated EDA, and dynamic chart generation. | Pandas + Matplotlib |
| **Visual Interpreter (VISION)** | 👁️ | Advanced image description and visual reasoning. | LLaMA Vision |
| **Global Researcher** | 🌐 | Real-time web search and Fact-checking. | DuckDuckGo Search |
| **Intelligent Router** | 🔀 | Context-aware query orchestration. | LLaMA 3.1 (8B) |

---

## 🛠️ Tech Stack & Architecture

This project leverages a **Modular Agentic Architecture**:

- **Brain**: LLaMA-3.3-70B-Versatile (Inference via **Groq**)
- **Memory**: 
    - **Vector Store**: ChromaDB for document embeddings.
    - **SQL Persistence**: SQLAlchemy (SQLite) for persistent chat history.
- **Frontend/Backend**: Consolidated **Streamlit** application.
- **Processing**: 
    - **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers).
    - **Vision**: LLaMA Scout Vision models.

---

## 📂 Project Structure

```text
ai-knowledge-copilot/
├── backend/
│   ├── agents/           # Multi-agent logic (RAG, Data, Vision, Research)
│   ├── database/         # SQLite & Vector store configurations
│   └── rag/              # PDF ingestion and chunking logic
├── uploads/              # Volatile storage for processed files
├── streamlit_app.py      # Main Consolidated Entry Point 🚀
├── requirements.txt      # Dependency specification
├── .env                  # Secrets & API Keys
└── README.md             # You are here
```

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/aatreyipanchal/ai-knowledge-copilot.git
cd ai-knowledge-copilot

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```
> [!TIP]
> Get your free API key at [console.groq.com](https://console.groq.com)

### 3. Launch the Copilot
```bash
streamlit run streamlit_app.py
```

---

## 🎨 Professional Use Cases

### 📂 Document Analysis
"Summarize the key financial risks mentioned in page 4 of the uploaded policy PDF."

### 📈 Data Science on Demand
"Analyze the attached Sales.csv. Show me a correlation heat map between Profit and Discount and give me 3 key insights."

### 🖼️ Visual Context
"Describe the chart in this image and explain the trend."

### 🌍 Global Research
"What is the current market sentiment for NVIDIA stock according to latest news?"

---

## 📝 Resume Summary for Developers

> Engineered a sophisticated Multi-Agent AI system using a modular architecture for Document Intelligence, Data Analysis, and Visual Reasoning. Implemented a RAG pipeline with ChromaDB and optimized inference using LLaMA 3.3 on Groq. Designed a persistent chat system with SQLite and a high-performance Streamlit UI, achieving zero-cost deployment and sub-second response times for complex queries.

---

## 📜 License
Integrated under the MIT License. See [LICENSE](LICENSE) for details.
