"""
A thin orchestration layer mapping LLM plan -> handler execution.
We avoid executing arbitrary code. Instead we provide a set of allowed handlers
and interpret the LLM plan to call them with safe params.
"""

import json
import logging
from .handlers import handler_csv_analysis, handler_scrape_wikipedia_highest_grossing, handler_duckdb_s3_query

logger = logging.getLogger(__name__)

ALLOWED_HANDLERS = {
    "csv_analysis": handler_csv_analysis,
    "scrape_wikipedia": handler_scrape_wikipedia_highest_grossing,
    "duckdb_query": handler_duckdb_s3_query,
}

def interpret_plan_and_execute(workdir: str, question_text: str, plan_json: str):
    """
    plan_json is expected to be JSON describing `task_type` and `details`.
    Example: {"task_type":"csv_analysis", "details":{"x":"Rank","y":"Peak","plot":True}}
    """
    try:
        plan = json.loads(plan_json)
    except Exception:
        # fallback: naive heuristics
        plan = {"task_type": "generic_analysis", "details": {}}

    task_type = plan.get("task_type", "generic_analysis")
    details = plan.get("details", {})

    handler = ALLOWED_HANDLERS.get(task_type)
    if not handler:
        return {"error": f"Task type {task_type} not supported."}

    # call handler
    try:
        result = handler(workdir, question_text, details)
        return result
    except Exception as e:
        logger.exception("Handler failed")
        return {"error": str(e)}
