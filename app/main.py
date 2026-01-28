import time
import io
from PIL import Image
import pandas as pd
from fastapi import FastAPI, UploadFile, Depends, HTTPException, File, Form
import tempfile
from app.schemas import QueryRequest, QueryResponse
from app.rag.vector import vectordb
from app.rag.images import extract_images_from_pdf, describe_image
from app.schemas import QueryRequest, QueryResponse
from app.rag.llm import llm
from app.security import verify_api_key
from app.utils.file_type import get_file_type
from app.rag.document_ingester import DocumentIngester
from app.utils.doc_extractors import (
    extract_text_from_docx,
    extract_text_from_pptx,
)

app = FastAPI(title="RAG Microservice")

@app.post("/query", response_model=QueryResponse)
async def query_rag(
    payload: QueryRequest,
    _: None = Depends(verify_api_key)
):
    is_admin = payload.user_id == "admin" or payload.is_admin
    filter_dict = None if is_admin else {"user_id": payload.user_id}
    docs = vectordb.similarity_search(payload.question, k=3, filter=filter_dict)
    context = "\n".join(doc.page_content for doc in docs)

    prompt = f"""
    Answer the question using only the context below.

    Context:
    {context}

    Question:
    {payload.question}
    """

    response = llm.invoke(prompt)
    return QueryResponse(answer=response.content)

@app.post("/ingest")
async def ingest(
        file: UploadFile,
        user_id: str = Form(...),
        _: None = Depends(verify_api_key)
    ):
    """Main ingestion endpoint with user context"""
    file_type = get_file_type(file.filename)

    if file_type is None:
        raise HTTPException(
            status_code=415,
            detail=f"File type not supported: {file.filename}"
        )
    
    file_bytes = await file.read()
    document_id = f"{user_id}_{file.filename}_{int(time.time())}"
    
    # Initialize ingester with user context
    ingester = DocumentIngester(
        user_id=user_id,
        document_id=document_id,
        filename=file.filename
    )
    # Handle each file type
    if file_type == "pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            pdf_path = tmp.name
        result = await ingester.ingest_pdf(pdf_path)
    
    elif file_type == "image":
        image = Image.open(io.BytesIO(file_bytes))
        result = await ingester.ingest_image(image)
    
    elif file_type == "text":
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid UTF-8")
        result = ingester.ingest_text(content, file_type="text")
    
    elif file_type == "docx":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_bytes)
            file_path = tmp.name
        content = extract_text_from_docx(file_path)
        result = ingester.ingest_text(content, file_type="docx")
    
    elif file_type == "pptx":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
            tmp.write(file_bytes)
            file_path = tmp.name
        content = extract_text_from_pptx(file_path)
        result = ingester.ingest_text(content, file_type="pptx")
    
    elif file_type == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes))
        result = ingester.ingest_csv(df)
    
    return result