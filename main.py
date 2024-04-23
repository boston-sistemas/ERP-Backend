from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from config.routing import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


@app.get("/")
async def home():
    return {"message": "MECSA - Sistema ERP"}

app.include_router(api_router, prefix=settings.API_V1_STR)