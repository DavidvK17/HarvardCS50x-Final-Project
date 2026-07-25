"""
This script, init_db.py, serves as the structural foundation and metadata ingestion pipeline for my full-stack application. 
Its primary objective is two-fold: first, it establishes a local SQLite database file, explicitly configuring the relational 
schema—including tables for corporate assets, index mappings, and the empty table structures for company fundamentals—with 
strict integrity constraints like foreign keys and cascading deletes. Second, it acts as an automated registry pipeline, 
leveraging the power of the pandas library to scrape live index constituents from Wikipedia, cross-referencing those discovered 
tickers with the official U.S. SEC master directory to safely fetch verified Central Index Key (CIK) codes, and seeding my database 
with a pristine baseline map of corporate identities.
"""

# Import the built-in sqlite3 library, allowing my Pythin script to communicate
# directly wih a localized SQL daabse engine using standard SQL syntax
import sqlite3

# Import the third-party request library, enabling my script to execute HHTP requests
# accross the internet to pull down structured raw data from remote servers
import requests

# Import the pandas library using the standard, idiomatic alias 'pd'. I leverage its robust, underlying HTML parsing capabilities to read Ib tables natively into DataFrames.
import pandas as pd

# Define a global constant for my local database filename
DB_NAME = "portfolio.db"

"""
Establish a global dictionary containing custom HTTP Headers. Remote servers like the SEC and Wikipedia
explicitly require an identifying 'User-Agent' string to prevent anonymous automated scrapers from causing
performance degradation
"""
HEADERS = {"User-Agent": "David Singer david.sing7@gmail.com"}

# Define a global array (list) containing the precise market indices my platform will track.
INDICES = ["SP500", "NASDAQ100", "DOW30"]

def get_index_tickers(index_type):
    # Scrapes, normalizes, and filters the component stock tockers for a given market index by extracting tabular data from live Wikipedia records.

    # Provides clear terminal feedback to the operator indicating which index processing loop has begun.
    print(f"Scanning current {index_type} components list via Wikipedia...")

    """
    Construct a divtionary acting as a key-value registry map.
    The key is the index identifier string, and the value is a tuple containing:
    1. The target URL hosting the public list.
    2. The exact string name of the table column housing the stock symbols
    """
    pages = {
        "SP500": (
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
            "Symbol"
        ),
        "NASDAQ100": (
            "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies",
            "Ticker"
        ),
        "DOW30": (
            "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
            "Symbol"
        )
    }

    # Defensive programming: validation check to ensure the requested index type exists in my dictionary
    # If the indext isn't reecognized, return an empty set immediately to prevent application crashes
    if index_type not in pages:
        return set()

    # Unpack the tuple asociated with my target index, assigning the Ib address to the variable 'url'
    # and the scpecifc target string header name to the variable 'ticker_column'
    url, ticker_column = pages[index_type]

    try:
        # Utilize the panas HTML craping engine to parse the remote Ip page
        # pd.read_html searches through the entire HTML DOM tree, automaticaaly isolates all tags
        # formatted as <table>, and returns them natively as a list of pandas DataFrame objects.
        # I pass my storage_options conaintinet the USer-Agent to satisfy remote server authentication
        tables = pd.read_html(
            url,
            storage_options={"User-Agent": HEADERS["User-Agent"]}
        )

        # Initialize an empty Python 'set'. I select a set rather than a list because a set
        # inherently guarantees uniqueness, preventing dublicate ticker representation in my memory allocation.
        tickers = set()

        # Iterate sequentially through the list of extracted tables found on the target Ib page.
        for table in tables:

            # Schema Check: If the exact column string name I need (e.g., 'Ticker' or 'Symbol') 
            # is not present in the current table's column index, skip it and continue checking the next table.
            if ticker_column not in table.columns:
                continue

            # If the correct column is found, loop through every individual entry inside that specific column.
            for value in table[ticker_column]:

                # Data Sanitization: Check if the current value is missing or null (NaN).
                # If it is empty, skip to the next row immediately to avoid running string operations on Null objects.
                if pd.isna(value):
                    continue

                # Cast the column data safely to a string, strip away any leading or trailing whitespace, 
                # and capitalize all letters to enforce string uniformity.
                ticker = str(value).strip().upper()

                # Handle an edge case unique to the Dow Jones page, where cells can contain composite 
                # descriptions separated by colons (e.g., "MMM: 3M"). I split the string at the colon 
                # and extract index 0 to retain only the isolated ticker symbol ("MMM").
                if ":" in ticker:
                    ticker = ticker.split(":")[0].strip()

                # Normalize corporate share-class formatting to match the U.S. SEC data standard. 
                # This replaces dot notations (e.g., "BRK.B") with clean hyphens (e.g., "BRK-B").
                ticker = ticker.replace(".", "-")

                # Add the finalized, clean ticker string to my tickers set.
                tickers.add(ticker)

            # Design Choice: Once I have found the primary constituent table and successfully 
            # iterated through its values, break completely out of the outer tables loop. 
            # This prevents my scraper from erroneously scanning trailing historical or summary tables.
            break

        # Log out the successful results of my extraction pass directly to the developer console.
        print(f"Discovered {len(tickers)} unique symbols in registry mapping.")
        return tickers

    except Exception as e:
        # Graceful degradation: If a network timeout or parsing anomaly occurs, catch the exception, 
        # display an explicit warning tag in the terminal, and return an empty set to keep the app running.
        print(f"❌ Error compiling target index elements: {e}")
        return set()



def initialize_database():
    """
    Establishes the SQLite physical database file, configures the relational schemas,
    and executes the primary data pipeline synchronization sequence.
    """
    print(f"Creating database file: {DB_NAME}...")

    # Establish a connection context manager to my localized database file. 
    # If portfolio.db does not exist, the sqlite3 engine initializes it on the filesystem automatically.
    conn = sqlite3.connect(DB_NAME)

    # Generate an active cursor object. The cursor acts as my pointer mechanism, 
    # executing direct SQL commands and fetching rows out of query buffers.
    cursor = conn.cursor()

    # Crucial Design Step: In SQLite, foreign key enforcement is turned off by default. 
        # I must explicitly execute this PRAGMA directive on every single runtime initialization 
        # to guarantee my database drops invalid relational inputs and maintains true strict data integrity.
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. CREATE THE ASSETS TABLE
    # This table stores the absolute master record for every distinct corporate entity tracked by my platform.
    # The 'ticker' and 'cik' columns are marked as UNIQUE to prevent redundant tracking of the same security.
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS assets (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   ticker TEXT UNIQUE NOT NULL,
                   name TEXT NOT NULL,
                   cik TEXT UNIQUE, -- SEC CIK code
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   );
                   """)
    
    # 2. CREATE THE FUNDAMENTALS TABLE
    # This table captures historical financial statistics tied directly to my assets.
    # 'FOREIGN KEY (asset_id) REFERENCES assets(id)' creates a formal dependency link back to the assets table.
    # 'ON DELETE CASCADE' is a vital guardrail: if a parent asset is ever purged from my tracking, 
    # all matching historical fundamentals records are cleaned up instantly by the engine, preventing orphaned data rows.
    # 'UNIQUE(asset_id, fiscal_year)' creates a composite unique constraint, ensuring that I never store two 
    # separate fundamental data rows for the same company in the exact same calendar year.
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS fundamentals (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   asset_id INTEGER NOT NULL,
                   fiscal_year INTEGER NOT NULL,
                   revenue REAL,
                   operating_income REAL,
                   operating_margin REAL, -- Calculated as (operating_income / revenue) * 100
                   revenue_growth REAL, -- Calculated YoY vs previous year
                   UNIQUE(asset_id, fiscal_year),
                   FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
                   );
                   """)

    # 3. CREATE THE ASSET INDEX MAPPING JUGGERNAUT TABLE
    # This acts as my relational bridge or 'junction table' to resolve a classic many-to-many relationship: 
    # an asset can exist within multiple indices simultaneously (e.g., Apple is in the S&P 500 AND the NASDAQ-100), 
    # and an index contains many individual assets.
    # A composite PRIMARY KEY is defined over both fields to ensure a specific asset-to-index link is never recorded twice.
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS asset_index_mapping (
                    asset_id INTEGER,
                    index_code TEXT,
                    PRIMARY KEY (asset_id, index_code),
                    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
                    );
                    """)

    # Commit my transactions to write the new physical tables securely to the database file structure.
    conn.commit()

    # Initialize a tracking dictionary to keep my scraped stock groups separated by index inside memory.
    index_maps = {}

    # Initialize an omnibus master set to pool every single unique stock ticker scraped across all indices combined.
    all_unique_tickers = set()

    # Loop dynamically through my global indices tracking array.
    for index in INDICES:
        # Fire my pandas parser for the current target index.
        tickers = get_index_tickers(index)

        # Store the individual results inside my dictionary mapping for later processing.
        index_maps[index] = tickers

        # Leverage the set '.update()' method to perform an in-memory set union operation. 
        # This appends all newly discovered symbols into my master pooling set while filtering out duplicates automatically.
        all_unique_tickers.update(tickers)
  
    print("Syncing master SEC directory maps...")
    try:
        # Connect to the official United States SEC API server to pull down the definitive company tickers map.
        sec_url = "https://www.sec.gov/files/company_tickers.json"
        sec_response = requests.get(sec_url, headers=HEADERS)

        if sec_response.status_code == 200:
            # Parse the incoming structured raw JSON payload into a navigable native Python dictionary format.
            sec_registry = sec_response.json()

            # Prepare an empty list container to act as a staging buffer for bulk database inserts.
            portfolio_seed = []

            # Deconstruct the SEC registry payload. The SEC structures this file as nested numbered objects.
            for _, item in sec_registry.items():

                # Extract and sanitize the current entry's ticker symbol.
                ticker = item['ticker'].upper().replace('.', '-')

                # Filtering Step: If the SEC company symbol exists inside my master Ib-scraped tracking set, 
                # I want it! I capture its metadata and ignore all other thousands of global US corporations.
                if ticker in all_unique_tickers:
                    # Append a cleanly formatted tuple containing the data columns to my database staging list.
                    # I use .zfill(10) to format the SEC CIK integer into a standard 10-digit zero-padded string 
                    # (e.g., 320193 becomes "0000320193"), ensuring complete consistency with all SEC filing lookups.
                    portfolio_seed.append((ticker, item['title'], str(item['cik_str']).zfill(10)))

            # Performance Optimization: Instead of executing hundreds of slow single INSERT statements, 
            # I invoke '.executemany()'. This pushes the entire batch list buffer down to the SQLite engine 
            # in a single low-level transaction block.
            # 'INSERT OR IGNORE' handles any constraint conflicts gracefully by skipping duplicates.
            cursor.executemany("""
                            INSERT OR IGNORE INTO assets (ticker, name, cik) VALUES (?, ?, ?);
                            """, portfolio_seed)

            # Save my changes to the database.
            conn.commit()

            print("Mapping relational connections betIen assets and market indices...")

            # Iterate over my stored dictionary items containing the separated index sets.
            for index, tickers in index_maps.items():
                for t in tickers:
                    # Query the database to retrieve the auto-generated unique internal ID assigned 
                    # to the current ticker during the bulk asset insert above.
                    cursor.execute("SELECT id FROM assets WHERE ticker = ?;", (t,))
                    row = cursor.fetchone()
                    # If the row lookup is successful, I have a complete relationship lock.
                    if row:
                        # Insert a new linking entry into my relational junction table, passing 
                        # the internal asset integer ID alongside the active string index code (e.g., 'NASDAQ100').
                        cursor.execute("INSERT OR IGNORE INTO asset_index_mapping (asset_id, index_code) VALUES (?, ?);", (row[0], index))

            # Finalize the transaction by committing all relational mappings safely to disk.
            conn.commit()
            print("System setup complete! All index tracks mapped successfully.")

    except Exception as e:
        # Capture and alert on any serious connection failures or network drops occurring during execution.
        print(f"❌ Critical system connection breakdown: {e}")
    finally:
        # Always clause: Regardless of whether the execution succeeded perfectly or threw errors, 
        # explicitly close my database connection file descriptor to prevent memory leaks or file locks.
        conn.close()

# Python boilerplate: Checks whether this script is being executed directly by the runtime 
# (e.g., python3 init_db.py). If it is, run my master initializer. If this file is merely imported 
# by another module, this execution block remains dormant.
if __name__ == "__main__":
    initialize_database()