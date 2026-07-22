import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(
    title = "Financial Portfolio Analytics API",
    description = "Enterprise REST-API for fetching SEC-Fundamentals for React-Frontend",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # to be replaced by URL later
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

DB_NAME = "portfolio.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/assets", response_model=List[Dict[str, Any]])
def get_assets():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, ticker, name, asset_type, allocation_eur, cik FROM assets;")
        assets = [dict(row) for row in cursor.fetchall()]
        return assets
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/api/fundamentals/{asset_id}", response_model=List[Dict[str, Any]])
def get_fundamentals_for_asset(asset_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
                       SELECT fiscal_year, revenue, operating_income, operating_margin, revenue_growth
                       FROM fundamentals
                       WHERE asset_id = ?
                       ORDER BY fiscal_year ASC;
                       """, (asset_id,))
        
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail=f"No fundamentals data for ASSET_ID {asset_id} found.")
        
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()