from fastapi import APIRouter

from app.api.endpoints import webhook

api_router = APIRouter()
api_router.include_router(webhook.router, tags=["webhook"])
