import os
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from backend.agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0.3)
        self.search_tool = DuckDuckGoSearchRun()

    def search(self, question: str, session_id: str = "default_session") -> dict:
        search_results = self.search_tool.run(question)
        
        system_prompt = f"""You are a research assistant for an AI Knowledge Copilot. 
        Based on the web search results, provide a clear, concise, and accurate answer.
        Always cite the search results as your source.
        
        Search Results:
        {search_results}
        """
        
        answer = self.run(question, session_id=session_id, system_prompt=system_prompt)
        
        return {"answer": answer, "sources": ["DuckDuckGo Web Search"]}

def run_research_agent(question: str, session_id: str = "default_session") -> dict:
    agent = ResearchAgent()
    return agent.search(question, session_id)
