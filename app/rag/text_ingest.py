from app.rag.vector import vectordb
from app.utils.chunking import chunk_text
from app.utils.markdown import strip_markdown

def ingest_text(content: str, filename:str, file_type: str):
    if filename.endswith(".md"):
        content = strip_markdown(content)
        
    chunks = chunk_text(content)

    texts = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        texts.append(chunk)
        metadatas.append({
            "source": "upload",
            "filename": filename,
            "type": file_type,
            "chunk": i + 1
        })

    vectordb.add_texts(texts, metadatas=metadatas)