from backend.agents.base_agent import BaseAgent
import pandas as pd
import io, base64, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

_dataframe_store: dict[str, pd.DataFrame] = {}

class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0)

    def analyze(self, question: str, session_id: str = "default_session", filename: str = None) -> dict:
        if not filename or filename == "":
            # Try to get the latest file from disk
            files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".csv")]
            if not files:
                return {"answer": "No CSV file loaded. Please upload a CSV first.", "chart": None}
            filename = sorted(files)[-1] # Simple latest logic

        df = _dataframe_store.get(filename)
        if df is None:
            # Try loading from disk
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                _dataframe_store[filename] = df
            else:
                return {"answer": f"File '{filename}' not found in storage.", "chart": None}

        schema_info = f"Columns: {list(df.columns)}\nShape: {df.shape}\nSample:\n{df.head(3).to_string()}"

        prompt = f"""You are a Python data analyst for an AI Knowledge Copilot. 
        Given this dataset info, write Python code to analyze it and answer the user's question clearly.
        If a chart or graph is requested, use matplotlib.pyplot (already imported as plt) to draw it. 
        The dataframe is already loaded as `df`. 
        
        Dataset info:
        {schema_info}
        
        Question: {question}
        
        Format your response exactly as follows:
        Answer: <your short text answer>
        ```python
        <your pandas/matplotlib python code here>
        ```
        """
        
        content = self.run(prompt, session_id=session_id)
        
        answer_text = content
        code_block = ""
        
        if "```python" in content:
            parts = content.split("```python")
            answer_text = parts[0].replace("Answer:", "").strip()
            code_block = parts[1].split("```")[0].strip()
        
        chart_base64 = None
        if code_block:
            local_env = {'df': df, 'pd': pd, 'plt': plt}
            try:
                exec(code_block, local_env)
                if plt.get_fignums():
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close('all')
            except Exception as e:
                answer_text += f"\n\n(Error executing data logic: {e})"
                
        return {"answer": answer_text, "chart": chart_base64}

def run_data_agent(question: str, session_id: str = "default_session", filename: str = None) -> dict:
    agent = DataAgent()
    return agent.analyze(question, session_id, filename)

def load_csv(file_bytes: bytes, filename: str) -> str:
    # Save to disk
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    # Load into memory
    df = pd.read_csv(io.BytesIO(file_bytes))
    _dataframe_store[filename] = df
    return filename

def get_loaded_files() -> list[str]:
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".csv")]
    return sorted(files)
