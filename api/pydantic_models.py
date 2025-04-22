from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ModelName(str, Enum):
    gemma = "gemma2-9b-it"
    llama8b = "llama-3.1-8b-instant"
    

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.gemma)  # Default model

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime

class DeleteFileRequest(BaseModel):
    file_id: int

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime
    file_size: int  # New field
    content_type: str  # New field
