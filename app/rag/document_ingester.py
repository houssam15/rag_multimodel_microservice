from typing import List, Dict, Any
from app.rag.vector import vectordb
from app.rag.images import extract_images_from_pdf, describe_image
from app.rag.llm import llm
import fitz

class DocumentIngester:
    """Unified ingester with metadata support for various document types."""
    def __init__(self,user_id: str,document_id: str,filename: str):
        self.user_id = user_id
        self.document_id = document_id
        self.filename = filename

    def _build_metadata(self, file_type:str, **kwargs) -> Dict[str,Any]:
        """Build base metadata with user context"""
        metadata = {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "filename": self.filename,
            "source": "upload",
            "file_type": file_type
        }
        metadata.update(kwargs)
        return metadata
    
    def _add_to_vectordb(self, texts: List[str], metadatas: List[Dict]):
        """Single point of entry to vector DB"""
        vectordb.add_texts(texts, metadatas=metadatas)

    async def ingest_pdf(self, pdf_path: str):
        """Handle PDF text and images in one method"""
        # Extract and ingest text
        text = self._extract_text_from_pdf(pdf_path)
        chunks = self._chunk_text(text)  # Optional: chunk text
        
        text_metadatas = [
            self._build_metadata("pdf", chunk_type="text", chunk_index=i)
            for i in range(len(chunks))
        ]
        self._add_to_vectordb(chunks, text_metadatas)
        
        # Extract and ingest images
        images = extract_images_from_pdf(pdf_path)
        captions = []
        image_metadatas = []
        
        for i, img in enumerate(images):
            caption = await describe_image(img)
            captions.append(caption)
            image_metadatas.append(
                self._build_metadata(
                    "pdf",
                    chunk_type="image",
                    page_number=i + 1
                )
            )
        
        if captions:
            self._add_to_vectordb(captions, image_metadatas)
        
        return {
            "status": "ingested",
            "type": "pdf",
            "text_chunks": len(chunks),
            "images": len(images)
        }
    
    # -------- TEXT INGESTION --------
    def ingest_text(self, content: str, file_type: str = "text"):
        """Handle plain text files"""
        chunks = self._chunk_text(content)
        
        metadatas = [
            self._build_metadata(file_type, chunk_type="text", chunk_index=i)
            for i in range(len(chunks))
        ]
        
        self._add_to_vectordb(chunks, metadatas)
        
        return {
            "status": "ingested",
            "type": file_type,
            "chunks": len(chunks)
        }
    
    # -------- IMAGE INGESTION --------
    async def ingest_image(self, image, filename: str = None):
        """Handle single image files"""
        caption = await describe_image(image)
        metadata = self._build_metadata(
            "image",
            chunk_type="image",
            original_filename=filename or self.filename
        )
        
        self._add_to_vectordb([caption], [metadata])
        
        return {
            "status": "ingested",
            "type": "image"
        }
    
    # -------- CSV INGESTION --------
    def ingest_csv(self, df):
        """Handle CSV files (example: convert rows to text)"""
        # Convert each row to descriptive text
        rows_as_text = [
            f"Row {i}: {row.to_dict()}"
            for i, row in df.iterrows()
        ]
        
        metadatas = [
            self._build_metadata("csv", chunk_type="row", row_index=i)
            for i in range(len(rows_as_text))
        ]
        
        self._add_to_vectordb(rows_as_text, metadatas)
        
        return {
            "status": "ingested",
            "type": "csv",
            "rows": len(rows_as_text)
        }
    
    # -------- UTILITY METHODS --------
    def _chunk_text(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Simple text chunking (replace with proper chunking if needed)"""
        words = content.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [content]

    def _extract_text_from_pdf(self,pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        return " ".join(page.get_text() for page in doc)
            
