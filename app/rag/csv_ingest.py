import csv
import io
from app.rag.vector import vectordb
from app.utils.chunking import chunk_text


def ingest_csv(file_bytes: bytes, filename: str):
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("CSV must be UTF-8 encoded")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    # Convert rows → readable text
    csv_text = "\n".join(
        ", ".join(cell for cell in row)
        for row in rows
    )

    chunks = chunk_text(csv_text)

    texts = [
        f"CSV file ({filename}) chunk {i+1}:\n{chunk}"
        for i, chunk in enumerate(chunks)
    ]

    vectordb.add_texts(texts)