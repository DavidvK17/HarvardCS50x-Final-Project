"""
This script, main.py, stands as the high-performance web server gateway for my full-stack application. 
Its primary purpose is to act as the communication bridge between my localized SQLite database and my 
Vue.js user interface. By leveraging the FastAPI framework, this file exposes clean, secure, and programmatic 
REST API endpoints. It listens for incoming HTTP network requests from the browser, decodes path and query 
parameters, executes efficient SQL queries to extract my curated asset and fundamental metrics, transforms 
raw database rows into JSON-compliant data structures, and manages Cross-Origin Resource Sharing (CORS) 
protocols to ensure smooth data delivery.
"""

import sqlite3

# Import FastAPI to construct the web application framework, and HTTPException 
# to elegantly return standard HTTP error status codes to the frontend client.
from fastapi import FastAPI, HTTPException

# Import CORSMiddleware so I can handle Cross-Origin Resource Sharing security headers, 
# which permits browsers to securely fetch data from this API even if hosted on different local ports.
from fastapi.middleware.cors import CORSMiddleware

# From the built-in typing module, import List, Dict, and Any to implement clear, professional 
# Python type hints that declare the structural blueprint of my API data payloads.
from typing import List, Dict, Any


# Instantiate my core web application interface using the FastAPI constructor, 
# configuring explicit metadata for documentation and version control.
app = FastAPI(
    title = "Financial Portfolio Analytics API",
    description = "REST API for fetching SEC-Fundamentals for Vue frontend",
    version = "1.0.0"
)

# Attach the CORS security configuration layer to my FastAPI web app container.
app.add_middleware(
    CORSMiddleware,
    # Allow requests from all origins globally using the wildcard string for development purposes. 
    # I recognize that this will be restricted to my specific production domain URL before going live.
    allow_origins = ["*"], # to be replaced by URL later
    # Instruct the browser to allow credentials, cookies, or authorization tokens to pass through securely.
    allow_credentials = True,
    # Allow all standard HTTP method verbs (GET, POST, PUT, DELETE) to interact with my server paths.
    allow_methods = ["*"],
    # Accept all types of incoming HTTP header metadata payloads transmitted by the frontend client.
    allow_headers = ["*"],
)

DB_NAME = "portfolio.db"

def get_db_connection():
    """
    Helper function that instantiates and configures a unique database connection 
    handle for an individual HTTP request lifecycle.
    """
    # Open a raw connection stream to my local SQLite file.
    conn = sqlite3.connect(DB_NAME)

    # Crucial Design Configuration: Modify the default tuple-based return behavior of SQLite. 
    # Setting the connection row_factory to sqlite3.Row allows me to access data fields using 
    # explicit string column names (like row['ticker']) rather than fragile numerical array indices.
    conn.row_factory = sqlite3.Row

    # Return the highly interactive, dictionary-like connection object.
    return conn

# Declare a GET routing decorator mapping to the '/api/assets' network path. 
# The response_model type hint informs FastAPI to validate and format my output as a list of dictionaries.
@app.get("/api/assets", response_model=List[Dict[str, Any]])
def get_assets(index: str = None):
    """
    Retrieves corporate equity assets from my database, supporting an optional 
    query filter to isolate stocks belonging to a specific market index.
    """
    # Open the database connection and generate a clean execution pointer cursor.
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if index:
            # If a specific index code is requested (e.g., ?index=SP500), perform an INNER JOIN.
            # This links the assets table to my relational junction table across matching integer IDs,
            # using a parameterized query tuple '(index,)' to completely protect my database from SQL injection.
            cursor.execute("""
                            SELECT a.id, a.ticker, a.name, a.cik
                            FROM assets a
                            JOIN asset_index_mapping m ON a.id = m.asset_id
                            WHERE m.index_code = ?;
                        """, (index,))
        else:
            # If no parameter filter is passed by the client, execute a clean, comprehensive scan 
            # to pull every single corporate equity asset mapped in my registry.
            cursor.execute("SELECT id, ticker, name, cik FROM assets;")

        # Performance Transformation: Use a list comprehension to iterate through the database row buffers. 
        # By calling dict(row), I transform each sqlite3.Row object directly into a standard Python 
        # key-value dictionary, ensuring it can be serialized flawlessly into standard JSON arrays for Vue.js.
        assets = [dict(row) for row in cursor.fetchall()]

        # Return the processed payload list back across the network to the browser.
        return assets
    
    except sqlite3.Error as e:
        # If the database engine encounters an internal failure, catch the exception and raise 
        # a standard HTTP 500 Server Error to protect the frontend client from an unhandled server crash.
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# Declare a dynamic GET routing decorator that captures a mandatory path parameter '{asset_id}'.
@app.get("/api/fundamentals/{asset_id}", response_model=List[Dict[str, Any]])
def get_fundamentals_for_asset(asset_id: int):
    """
    Fetches the entire historical annual financial performance matrix for a specific 
    corporate asset, ordered chronologically by fiscal year.
    """
    # Open the database connection and spin up a structural query pointer.
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute an explicit lookup query targeting rows matching the passed asset_id integer.
        # I force an 'ORDER BY fiscal_year ASC' clause to guarantee that my financial data blocks 
        # flow sequentially from the oldest year to the newest year, which is crucial for frontend charting.
        cursor.execute("""
                       SELECT fiscal_year, revenue, operating_income, operating_margin, revenue_growth
                       FROM fundamentals
                       WHERE asset_id = ?
                       ORDER BY fiscal_year ASC;
                       """, (asset_id,))

        # Extract the entire matching array buffer out of the database engine.
        rows = cursor.fetchall()
        # Validation Boundary: If the resulting array is completely empty, it means the requested asset ID 
        # does not exist or has not run through my SEC extraction pipeline yet. Raise an HTTP 404 error.
        if not rows:
            raise HTTPException(status_code=404, detail=f"No fundamentals data for ASSET_ID {asset_id} found.")

        # Map the SQLite row collection into clean dictionary elements and pass them directly to the client.
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        # Catch and intercept unexpected internal SQLite operation errors safely.
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()