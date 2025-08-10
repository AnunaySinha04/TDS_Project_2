# api/index.py
from fastapi import FastAPI
from fastapi import FastAPI
from app.router import router  # wherever your routes are

app = FastAPI()
app.include_router(router)

handler = app  # Required by Vercel

@app.get("/")
def root():
    return {"message": "Data Analyst Agent is running"}

# This is needed for Vercel's Python runtime
handler = app
