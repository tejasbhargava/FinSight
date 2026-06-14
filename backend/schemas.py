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


class CompareRequest(BaseModel):
    company1: str
    company2: str
    question: str
    chat_history: List[Message] = []


class QueryResponse(BaseModel):
    answer: str
    tools_used: List[str]
    sources: List[str] = Field(default_factory=list)


class CompareResponse(BaseModel):
    comparison: str
    tools_used: List[str]
    sources: List[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    status: str
    ticker: str
    chunks: int

class ThesisRequest(BaseModel):
    company: str
    chat_history: List[Message] = []


class ThesisResponse(BaseModel):
    report: str
    tools_used: List[str]
    sources: List[str]

class PDFRequest(BaseModel):
    company: str
    report: str