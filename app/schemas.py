from pydantic import BaseModel
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    question: str
    user_id: str
    is_admin: bool = False  

class ChunkContext(BaseModel):
    text: str
    position: Dict[str, Any]

class QueryResponse(BaseModel):
    answer: str
    context: List[ChunkContext]