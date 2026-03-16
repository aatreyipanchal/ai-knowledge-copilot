import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "./chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def get_vectorstore():
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )

def get_retriever(k: int = 3):
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})
