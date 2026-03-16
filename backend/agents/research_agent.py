import os
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage

search_tool = DuckDuckGoSearchRun()

def run_research_agent(question: str) -> dict:
    # Step 1: Search the web
    search_results = search_tool.run(question)

    # Step 2: Summarize with LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
        streaming=True,
    )

    prompt = f"""You are a research assistant. Based on the search results below, give a clear and concise answer.
Always mention key facts and figures. End with a brief summary.

Search Results:
{search_results}

Question: {question}

Answer:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content, "sources": ["DuckDuckGo Search"]}
