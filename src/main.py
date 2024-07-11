from core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routing import api_router
from fastapi.staticfiles import StaticFiles
# from src.core.database import Base, engine
#
# def create_tables():
#     Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

origins=[
    "http:localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup_event():
#     create_tables()

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
async def home():
    return {"message": "MECSA - Sistema ERP"}


app.include_router(api_router)
