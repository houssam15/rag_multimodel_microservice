from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    user_id: str
    is_admin: bool = False  

class QueryResponse(BaseModel):
    answer: str