from PIL import Image
from app.rag.images import describe_image
from app.rag.vector import vectordb
import io

def ingest_image(file_bytes: bytes, filename: str):
    image = Image.open(io.BytesIO(file_bytes))
    caption = describe_image(image)

    vectordb.add_texts(
        [caption],
        metadatas=[{
            "source": "upload",
            "filename": filename,
            "type": "image"
        }]
    )
