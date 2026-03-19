from backend.agents.base_agent import BaseAgent

ROUTE_PROMPT = """You are a query router for an AI Knowledge Copilot. 
Classify the user's question into exactly ONE category based on the intent and uploaded files.

Categories:
- RAG       → Questions about uploaded PDFs, documents, policies, or general knowledge within stored docs.
- DATA      → Questions about CSV files, spreadsheets, statistics, trends, or requests for data visualization.
- IMAGE     → Questions about uploaded images, requests to describe pictures, or OCR tasks.
- RESEARCH  → General knowledge, current events, or queries requiring a web search.

IMPORTANT: Respond with ONLY one word: RAG, DATA, IMAGE, or RESEARCH.

Question: {question}
Category:"""

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__(model_name="llama-3.1-8b-instant", temperature=0)

    def route(self, question: str, filename: str = None) -> str:
        """Returns 'RAG', 'DATA', 'IMAGE', or 'RESEARCH'"""
        
        # Extension-based routing is a strong signal
        if filename:
            ext = filename.lower()
            if ext.endswith(".pdf"):
                return "RAG"
            if ext.endswith(".csv"):
                return "DATA"
            if ext.endswith((".png", ".jpg", ".jpeg")):
                return "IMAGE"

        response = self.llm.invoke(ROUTE_PROMPT.format(question=question))
        route = response.content.strip().upper()

        if route not in ("RAG", "DATA", "IMAGE", "RESEARCH"):
            # Simple keyword fallback if LLM misses
            lower_q = question.lower()
            if any(ext in lower_q for ext in [".csv", "data", "stats", "chart", "plot"]):
                return "DATA"
            if any(ext in lower_q for ext in [".pdf", "document", "file", "read"]):
                return "RAG"
            if any(ext in lower_q for ext in ["image", "picture", "photo", "see", "look"]):
                return "IMAGE"
            return "RESEARCH"
        return route

def route_query(question: str, filename: str = None) -> str:
    router = RouterAgent()
    return router.route(question, filename=filename)
