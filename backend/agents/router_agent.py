import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

ROUTE_PROMPT = """You are a query router. Classify the user's question into exactly ONE category.

Categories:
- RAG       → question about uploaded documents, PDFs, files, policies, manuals
- DATA      → question about CSV data, spreadsheets, numbers, statistics, trends
- RESEARCH  → general knowledge, current events, web search needed

Respond with ONLY one word: RAG, DATA, or RESEARCH

Question: {question}
Category:"""

def route_query(question: str) -> str:
    """Returns 'RAG', 'DATA', or 'RESEARCH'"""
    # Use the small fast model just for routing
    llm = ChatGroq(
        model="llama-3.1-8b-instant",   # Fast + cheap for simple classification
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=5,
    )
    response = llm.invoke([HumanMessage(content=ROUTE_PROMPT.format(question=question))])
    route = response.content.strip().upper()

    # Fallback safety
    if route not in ("RAG", "DATA", "RESEARCH"):
        return "RESEARCH"
    return route
