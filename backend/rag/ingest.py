from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.database.vector_store import get_vectorstore
import tempfile, os

def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    """Ingest a PDF file into the vector store. Returns number of chunks stored."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(documents)

        # Tag each chunk with source filename
        for chunk in chunks:
            chunk.metadata["source"] = filename

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

        return len(chunks)
    finally:
        os.unlink(tmp_path)
