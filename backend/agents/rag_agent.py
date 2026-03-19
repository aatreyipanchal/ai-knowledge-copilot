from backend.agents.base_agent import BaseAgent
from backend.database.vector_store import get_retriever

class RAGAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0.1)

    def query(self, question: str, session_id: str = "default_session", filename: str = None) -> dict:
        retriever = get_retriever(k=4, filename=filename)
        docs = retriever.invoke(question)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})
        
        system_prompt = f"""You are a Premium AI Knowledge Copilot. 
        Answer the question using ONLY the provided context. 
        
        Guidelines:
        - Use ## Headings for major points.
        - Use **Markdown Tables** or bullet points for comparisons or lists.
        - Cite your sources clearly at the end in a **Sources** section.
        - If the answer isn't in the context, say "I couldn't find that in the uploaded documents."
        
        Context:
        {context}
        """
        
        answer = self.run(question, session_id=session_id, system_prompt=system_prompt)
        
        return {"answer": answer, "sources": sources}

def run_rag_agent(question: str, session_id: str = "default_session", filename: str = None) -> dict:
    agent = RAGAgent()
    return agent.query(question, session_id, filename)