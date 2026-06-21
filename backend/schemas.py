from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class IngestRequest(BaseModel):
    company: str
    form_type: str = "10-K"

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class QueryRequest(BaseModel):
    company: str
    question: str
    chat_history: List[Message] = []
    session_id: int | None = None


class CompareRequest(BaseModel):
    company1: str
    company2: str
    question: str
    chat_history: List[Message] = []
    session_id: int | None = None


class QueryResponse(BaseModel):
    answer: str
    tools_used: List[str]
    sources: List[str] = Field(default_factory=list)
    session_id: int


class CompareResponse(BaseModel):
    comparison: str
    tools_used: List[str]
    sources: List[str] = Field(default_factory=list)
    session_id: int


class IngestResponse(BaseModel):
    status: str
    ticker: str
    chunks: int

class ThesisRequest(BaseModel):
    company: str
    chat_history: List[Message] = []
    session_id: int | None = None


class ThesisResponse(BaseModel):
    report: str
    tools_used: List[str]
    sources: List[str]
    session_id: int 

class PDFRequest(BaseModel):
    company: str
    report: str