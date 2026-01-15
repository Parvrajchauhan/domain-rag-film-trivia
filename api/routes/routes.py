from fastapi import APIRouter
from api.schemas import QueryRequest, QueryResponse
from api.core.generator import generate
import api.core.model_store as model_store

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_movie(req: QueryRequest):
    result = generate(req.query,model_store.judge_model)
    return result
