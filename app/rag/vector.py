from langchain_chroma import Chroma
from .llm import embeddings

vectordb = Chroma(
    collection_name="rag_docs",
    embedding_function=embeddings,
    persist_directory="../../chroma_db"
)