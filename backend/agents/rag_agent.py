from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.database.vector_store import get_retriever
import os

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful enterprise assistant. Answer the question using ONLY the context below.
If the answer isn't in the context, say "I couldn't find that in the uploaded documents."

Context:
{context}

Question: {question}

Answer:""",
)

def get_rag_chain():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True,
        temperature=0.2,
    )
    retriever = get_retriever(k=3)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": RAG_PROMPT},
        return_source_documents=True,
    )
    return chain

def run_rag_agent(question: str) -> dict:
    chain = get_rag_chain()
    result = chain.invoke({"query": question})
    sources = list({doc.metadata.get("source", "unknown") for doc in result["source_documents"]})
    return {"answer": result["result"], "sources": sources}
