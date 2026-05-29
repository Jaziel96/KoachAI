from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(title="Koach", version="0.1.0")
app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "project": "koach"}
