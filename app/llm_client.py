from openai import OpenAI
from .config import OPENAI_API_KEY, OPENAI_BASE_URL
import logging

logger = logging.getLogger(__name__)

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. Please set environment variable.")

# init OpenAI-compatible client with base_url
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

def plan_task_with_llm(question_text: str, files_list: list) -> str:
    """
    Ask LLM to produce a short plan: returns the LLM text output.
    We request a concise JSON plan describing steps; the code will strictly
    interpret keywords (scrape, csv, duckdb_query, plot, regression).
    """
    system = (
        "You are a concise data analyst planner. Read the question and available files. "
        "Return a JSON object with keys: 'task_type' and 'details'. "
        "task_type one of: scrape, csv_analysis, duckdb_query, generic_analysis. "
        "details: short instruction for handlers. Respond only with JSON."
    )
    user = f"Question:\n{question_text}\nFiles: {', '.join(files_list)}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # model choice can be changed as available
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.0,
        max_tokens=400,
    )
    return response.choices[0].message.content

def format_final_with_llm(question_text: str, interim: dict, expected_format: str = "array") -> str:
    """
    Optionally use the LLM to produce the final answer text given interim results.
    We call it with low temperature to get deterministic format.
    """
    system = (
        "You will be given the original question and interim JSON results. "
        "Return ONLY the final answer in the exact schema requested by the question. "
        "If the question asks for a JSON array, return an array; if an object, return an object. No prose."
    )
    user = {
        "question": question_text,
        "interim": interim,
        "expected_format": expected_format
    }
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": str(user)}
        ],
        temperature=0.0,
        max_tokens=800,
    )
    return resp.choices[0].message.content
