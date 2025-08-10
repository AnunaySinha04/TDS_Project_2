from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile
import json

from .llm_client import plan_task_with_llm, format_final_with_llm
from .worker import interpret_plan_and_execute
from .config import AGENT_TIMEOUT_SEC

router = APIRouter()

@router.post("/api/")
async def api(files: List[UploadFile] = File(...)):
    # find questions.txt
    qfile = next((f for f in files if f.filename and f.filename.lower().endswith("questions.txt")), None)
    if not qfile:
        raise HTTPException(status_code=400, detail="questions.txt is required")

    with tempfile.TemporaryDirectory() as workdir:
        # save files
        saved = []
        for f in files:
            path = os.path.join(workdir, f.filename)
            with open(path, "wb") as out:
                out.write(await f.read())
            saved.append(f.filename)

        qpath = os.path.join(workdir, "questions.txt")
        with open(qpath, "r", encoding="utf-8", errors="ignore") as r:
            question_text = r.read()

        # 1) ask LLM for a plan
        try:
            plan_text = plan_task_with_llm(question_text, saved)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM planning failed: {e}")

        # 2) execute the plan with safe handlers
        interim = interpret_plan_and_execute(workdir, question_text, plan_text)

        # 3) optionally ask LLM to format final result in requested schema
        try:
            # We guess expected format from question text; default to "array"
            expected_format = "array" if "array" in question_text.lower() else "object"
            final_text = format_final_with_llm(question_text, interim, expected_format)
            # try parse JSON, else return interim
            try:
                final_obj = json.loads(final_text)
                return final_obj
            except Exception:
                # fallback return interim
                return {"interim": interim, "final_text": final_text}
        except Exception as e:
            # If formatting fails, return interim
            return {"interim": interim}
