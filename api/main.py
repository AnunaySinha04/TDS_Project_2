from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
from data_agent import process_query

app = FastAPI()

@app.post("/")
async def analyze_data(file: UploadFile = File(...), query: str = Form(...)):
    try:
        # Read file into DataFrame
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Run your Data Analyst Agent logic
        result = process_query(df, query)
        return JSONResponse({"status": "success", "result": result})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# Required for Vercel
handler = app
