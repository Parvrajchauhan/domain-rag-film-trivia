from fastapi import FastAPI
from api.routes.routes import router

app = FastAPI(
    title="Film Trivia RAG API",
    version="1.0.0"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
