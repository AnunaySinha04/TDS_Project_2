import pandas as pd
import os
from openai import OpenAI

BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)

def process_query(df: pd.DataFrame, query: str) -> str:
    # Convert data to markdown table (sample rows only to avoid token overflow)
    preview = df.head(10).to_markdown()

    prompt = f"""
    You are a data analyst.
    Dataset sample:
    {preview}

    Question:
    {query}

    Provide an analysis based on the full dataset, not just the preview.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a skilled data analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
