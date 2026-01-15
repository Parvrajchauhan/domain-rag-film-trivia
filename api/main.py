from fastapi import FastAPI
from api.routes.routes import router
from src.test.exact_match import load_judge_model
import api.core.model_store as model_store
from src.embedding.embedding_model import load_embedding_model




app = FastAPI(
    title="Film Trivia RAG API",
    version="1.0.0"
)
app = FastAPI()

@app.on_event("startup")
def load_models():

    model_store.embedding_model = load_embedding_model()
    model_store.judge_model = load_judge_model()

    print(" Embedding model loaded")
    print(" Judge model loaded")

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
