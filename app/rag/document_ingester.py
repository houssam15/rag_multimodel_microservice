from typing import List, Dict, Any
from app.rag.vector import vectordb
from app.rag.images import extract_images_from_pdf, describe_image
from app.rag.llm import llm
import fitz
import json

class DocumentIngester:
    """Unified ingester with metadata support for various document types."""
    def __init__(self,user_id: str,document_id: str,filename: str,file_id:str):
        self.user_id = user_id
        self.document_id = document_id
        self.filename = filename
        self.file_id = file_id

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
        #implement chunking blocks 
        blocks = self._extract_blocks_from_pdf(pdf_path)
        chunks = self._chunk_blocks(blocks)
        # Extract and ingest text
        # text = self._extract_text_from_pdf(pdf_path)
        #chunks = self._chunk_text(text)  # Optional: chunk text
        texts = [chunk["text"] for chunk in chunks]
        text_metadatas = [
            self._build_metadata(
                "pdf", 
                chunk_type="text",
                chunk_index=i,
                chunk_position=json.dumps(chunk["position"]),
                file_id=self.file_id 
            )
            for i, chunk in enumerate(chunks)
        ] 
        self._add_to_vectordb(texts, text_metadatas)
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
                    page_number=i + 1,
                    file_id=self.file_id 
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

    def _make_bounding_rect(self, rects, width, height):
        return {
            "x1": min(r["x1"] for r in rects),
            "y1": min(r["y1"] for r in rects),
            "x2": max(r["x2"] for r in rects),
            "y2": max(r["y2"] for r in rects),
            "width": width,
            "height": height
        }
    
    def _chunk_blocks(self,blocks:List[Dict],chunk_size:int = 1000):
        chunks = []
        current_text = ""
        current_rects = []  
        current_page = None 
        current_width = 0
        current_height = 0  
        def flush_chunk():
            chunks.append({
                "text": current_text.strip(),
                "position": {
                    "boundingRect": self._make_bounding_rect(
                        current_rects, current_width, current_height
                    ),
                    "rects": current_rects,
                    "pageNumber": current_page
                }
            })
        for block in blocks:
            block_text = block["text"]
            if len(current_text) + len(block_text) >= chunk_size:
                flush_chunk()
                current_text= ""
                current_rects = []   
            current_text += block_text + " "
            current_rects.append({
                "x1": block["bbox"][0],
                "y1": block["bbox"][1],
                "x2": block["bbox"][2],
                "y2": block["bbox"][3],
                "width": block["width"],
                "height": block["height"]
            })
            current_page = block["page"]
            current_width = block["width"]
            current_height = block["height"]
        if current_text:
            flush_chunk()
        return chunks


    def _extract_text_from_pdf(self,pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        return " ".join(page.get_text() for page in doc)

    def _extract_blocks_from_pdf(self,pdf_path: str):
        doc = fitz.open(pdf_path)
        blocks = []
        for page_index, page in enumerate(doc):
            page_width = page.rect.width
            page_height = page.rect.height
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block:
                    continue
                text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        text += span["text"] + " "
                blocks.append({
                    "text": text.strip(),
                    "bbox": block["bbox"],
                    "page": page_index + 1,
                    "width": page_width,
                    "height": page_height 
                })
        return blocks
        
            
