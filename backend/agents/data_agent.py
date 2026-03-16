import pandas as pd
import io, os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

_dataframe_store: dict[str, pd.DataFrame] = {}

def load_csv(file_bytes: bytes, filename: str) -> str:
    df = pd.read_csv(io.BytesIO(file_bytes))
    _dataframe_store[filename] = df
    return filename

def get_loaded_files() -> list[str]:
    return list(_dataframe_store.keys())

def run_data_agent(question: str, filename: str = None) -> dict:
    if filename is None:
        files = get_loaded_files()
        if not files:
            return {"answer": "No CSV file loaded. Please upload a CSV first.", "chart": None}
        filename = files[-1]

    df = _dataframe_store.get(filename)
    if df is None:
        return {"answer": f"File '{filename}' not found.", "chart": None}

    # Build a compact schema summary for the LLM
    schema_info = f"Columns: {list(df.columns)}\nShape: {df.shape}\nSample:\n{df.head(3).to_string()}\n\nStats:\n{df.describe().to_string()}"

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )

    prompt = f"""You are a data analyst. Given this dataset info, answer the user's question clearly.
If computation is needed, reason step by step using the stats/sample provided.

Dataset info:
{schema_info}

Question: {question}

Answer concisely and include key numbers where relevant."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content, "chart": None}
