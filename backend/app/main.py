from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Koach", version="0.1.0")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "project": "koach"}
