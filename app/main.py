from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging
from .router import router
from .config import AGENT_TIMEOUT_SEC

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Data Analyst Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "POST multipart: questions.txt required + optional files (csv, parquet, image)."}
