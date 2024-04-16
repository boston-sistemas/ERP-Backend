from fastapi import FastAPI, APIRouter

from config.settings import settings
from config.routing import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

@app.get("/")
async def home():
    return {"message": "MECSA - Sistema ERP"}

app.include_router(api_router, prefix=settings.API_V1_STR)