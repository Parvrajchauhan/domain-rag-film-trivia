from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    query: str

class SourceDoc(BaseModel):
    id: str
    title: str
    source: str
    section:str
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]
    hallucination_score: float
    latency_ms: float
    confidence: float