"""
Handlers implement permitted operations. Each handler accepts the working_dir,
the parsed question text and a params dict (if needed), and returns a dict
containing intermediate results that will be assembled into the final answer.
"""

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import duckdb
from .utils import plot_scatter_with_regression
from .config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def handler_scrape_wikipedia_highest_grossing(_: str, question: str, params: dict):
    # simple scrapper for the sample wikipedia page. Returns a dataframe + simple stats
    url = params.get("url") or "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    resp = requests.get(url, headers={"User-Agent": "DataAgent/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find first wikitable
    table = soup.find("table", {"class": "wikitable"})
    if table is None:
        return {"error": "No table found on the page."}
    df = pd.read_html(str(table))[0]
    # Normalize columns if present: Rank, Peak, Worldwide gross etc
    # Attempt to coerce numeric columns
    colnames = [c for c in df.columns]
    # We'll try to find columns for Rank and Peak
    rank_col = next((c for c in colnames if "Rank" in str(c) or "rank" in str(c)), colnames[0])
    peak_col = next((c for c in colnames if "Peak" in str(c) or "peak" in str(c)), None)
    # Some pages have 'Peak' maybe not; try other heuristics
    # Return the dataframe head and some derived stats:
    return {"table_head": df.head(10).to_dict(orient="records"), "columns": colnames}

def handler_csv_analysis(workdir: str, question: str, params: dict):
    """
    Loads any CSVs in the workdir and runs requested operations:
    - correlation/regression of specified columns
    - plotting
    params example: {"x": "Rank", "y": "Peak", "plot": True}
    """
    # find csv in workdir
    csvs = [f for f in os.listdir(workdir) if f.lower().endswith(".csv")]
    if not csvs:
        return {"error": "No csv file uploaded."}
    path = os.path.join(workdir, csvs[0])
    df = pd.read_csv(path)
    out = {}
    xcol = params.get("x")
    ycol = params.get("y")
    if xcol and ycol and xcol in df.columns and ycol in df.columns:
        sub = df[[xcol, ycol]].dropna()
        corr = sub[xcol].corr(sub[ycol])
        out["correlation"] = float(corr)
        if params.get("plot"):
            plot_uri, size = plot_scatter_with_regression(sub[xcol].values, sub[ycol].values,
                                                           xlabel=xcol, ylabel=ycol)
            out["plot"] = {"data_uri": plot_uri, "size": size}
    else:
        out["columns"] = list(df.columns)
        out["rows"] = min(5, len(df))
    return out

def handler_duckdb_s3_query(_: str, question: str, params: dict):
    """
    Run a DuckDB query against S3 parquet (using httpfs). params: {"sql": "...", "s3_base": "s3://..."}
    Requires environment AWS keys if private bucket.
    """
    sql = params.get("sql")
    if not sql:
        return {"error": "No SQL provided."}
    con = duckdb.connect()
    # setup httpfs with AWS keys if provided
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            con.execute(f"SET s3_access_key_id='{AWS_ACCESS_KEY_ID}';")
            con.execute(f"SET s3_secret_access_key='{AWS_SECRET_ACCESS_KEY}';")
            con.execute(f"SET s3_region='{AWS_REGION}';")
        # enable parquet extension
        con.execute("INSTALL parquet; LOAD parquet;")
        res = con.execute(sql).fetchall()
        cols = [c[0] for c in con.description]
        # convert to list of dicts
        out = [dict(zip(cols, row)) for row in res]
        return {"rows": out}
    finally:
        con.close()
