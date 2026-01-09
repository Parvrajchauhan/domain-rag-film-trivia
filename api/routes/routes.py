from fastapi import APIRouter
from api.schemas import QueryRequest, QueryResponse
from api.core.generator import generate
from src.test.exact_match import load_judge_model

router = APIRouter()

judge = load_judge_model()

@router.post("/query", response_model=QueryResponse)
def query_movie(req: QueryRequest):
    result = generate(req.query,judge)
    return result
