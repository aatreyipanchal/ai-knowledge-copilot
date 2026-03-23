from backend.agents.base_agent import BaseAgent
import pandas as pd
import io, base64, os, contextlib
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
        if not filename:
            # Try to get the latest file from disk
            files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".csv")]
            if not files:
                return {"answer": "No CSV file loaded. Please upload a CSV first.", "charts": []}
            filename = sorted(files)[-1] # Simple latest logic
        
        # If a filename was provided but it's not a CSV, we shouldn't continue
        if not filename.lower().endswith(".csv"):
             return {"answer": f"Selected file '{filename}' is not a CSV. Data Agent only works with CSVs.", "charts": []}

        df = _dataframe_store.get(filename)
        if df is None:
            # Try loading from disk
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                _dataframe_store[filename] = df
            else:
                return {"answer": f"File '{filename}' not found in storage.", "charts": []}

        # Enrich diagnostic info
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        describe_str = df.describe(include='all').to_string()
        null_str = df.isnull().sum().to_string()
        
        enriched_info = f"""
        - Data Types and Info: 
        {info_str}
        - Null values: 
        {null_str}
        - Statistical Summary: 
        {describe_str}
        - Data Sample:
        {df.head(5).to_string()}
        """

        prompt = f"""You are a World-Class Data Scientist and Lead Analyst for an AI Knowledge Copilot. 
        Analyze the dataset based on the user's specific intent.
        
        IMPORTANT RULES:
        1. DATASET: Already loaded for you in variable `df`. DO NOT use `pd.read_csv`.
        2. USER INTENT (CRITICAL): 
           - If the user asks a simple, specific question (e.g., 'show first 5 rows', 'column list', 'count of nulls', 'mean of X'), provide ONLY that information briefly. 
           - If the user asks for 'EDA', 'Analysis', or any open-ended question, THEN perform a full DEEP analysis.
        3. ANALYSIS QUALITY (for deep analysis):
           - Provide Summary Statistics and Categorical Analysis.
           - Include Correlation Matrices with insights.
           - If a target exists (e.g., 'Survived'), analyze its relationship with other features.
        4. VISUALIZATION:
           - Generate charts ONLY if they add value or are explicitly requested. 
           - For simple data retrieval (like 'first 5 rows'), DO NOT generate charts.
           - Use `plt.figure(figsize=(...))` for each plot. 
           - If plotting two columns, ensure they are aligned and handled for NaNs: `df.dropna(subset=['A', 'B'])`.
        
        Dataset Context:
        - Filename: {filename}
        {enriched_info}
        
        User Question: {question}
        
        Format your response as follows:
        Answer: 
        ## [Title]
        [Detailed markdown response with insights, bullet points, and **markdown tables** for key data]
        
        [If applicable: "Based on the analysis, here is what I found..."]
        
        ```python
        import matplotlib.pyplot as plt
        # Use 'df' directly. 
        # For calculations, you can print() results to help your summary, 
        # but the FINAL answer must be in the markdown section above.
        [your python code here]
        ```
        """
        
        content = self.run(prompt, session_id=session_id)
        
        answer_text = content
        code_block = ""
        
        if "```python" in content:
            parts = content.split("```python")
            answer_text = parts[0].replace("Answer:", "").strip()
            code_block = parts[1].split("```")[0].strip()
        
        charts_base64 = []
        captured_output = ""
        
        if code_block and code_block.strip() and len(code_block.strip().split('\n')) > 1: # Check if there's more than just a placeholder
            local_env = {'df': df, 'pd': pd, 'plt': plt}
            output_buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(output_buffer):
                    exec(code_block, local_env)
                
                captured_output = output_buffer.getvalue()
                
                # Capture ALL open figures
                for i in plt.get_fignums():
                    plt.figure(i)
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    charts_base64.append(base64.b64encode(buf.read()).decode('utf-8'))
                plt.close('all')
            except Exception as e:
                answer_text += f"\n\n(Error executing data logic: {e})"
            finally:
                output_buffer.close()
        
        # We only show captured output if it's small or explicitly needed.
        # Otherwise, the LLM should have summarized it in the answer.
        if captured_output and len(captured_output.strip()) > 0:
            if len(captured_output.split('\n')) < 20: # Only show small text outputs
                 answer_text += f"\n\n**Additional Details:**\n```text\n{captured_output}\n```"
                
        return {"answer": answer_text, "charts": charts_base64}

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
