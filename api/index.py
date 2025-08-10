# api/index.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Data Analyst Agent is running"}

# This is needed for Vercel's Python runtime
handler = app
