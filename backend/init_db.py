import sqlite3
import requests
import pandas as pd

DB_NAME = "portfolio.db"
HEADERS = {"User-Agent": "David Singer david.sing7@gmail.com"}
INDICES = ["SP500", "NASDAQ100", "DOW30"]

def get_index_tickers(index_type):
    print(f"Scanning current {index_type} components list via Wikipedia...")

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

    if index_type not in pages:
        return set()

    url, ticker_column = pages[index_type]

    try:
        # Read every table on the page
        tables = pd.read_html(
            url,
            storage_options={"User-Agent": HEADERS["User-Agent"]}
        )

        tickers = set()

        for table in tables:

            if ticker_column not in table.columns:
                continue

            for value in table[ticker_column]:

                if pd.isna(value):
                    continue

                ticker = str(value).strip().upper()

                # DOw pages has "MMM: 3M"
                if ":" in ticker:
                    ticker = ticker.split(":")[0].strip()

                ticker = ticker.replace(".", "-")

                tickers.add(ticker)

            break

        print(f"Discovered {len(tickers)} unique symbols in registry mapping.")
        return tickers

    except Exception as e:
        print(f"❌ Error compiling target index elements: {e}")
        return set()



def initialize_database():
    print(f"Creating database file: {DB_NAME}...")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Enable foreign keys 
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Assets Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS assets (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   ticker TEXT UNIQUE NOT NULL,
                   name TEXT NOT NULL,
                   cik TEXT UNIQUE, -- SEC CIK code
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   );
                   """)
    
    # Fundamentals Table
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

    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS asset_index_mapping (
                    asset_id INTEGER,
                    index_code TEXT,
                    PRIMARY KEY (asset_id, index_code),
                    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
                    );
                    """)

    conn.commit()

    index_maps = {}
    all_unique_tickers = set()

    for index in INDICES:
        tickers = get_index_tickers(index)
        index_maps[index] = tickers
        all_unique_tickers.update(tickers)
  
    print("Syncing master SEC directory maps...")
    try:
        sec_url = "https://www.sec.gov/files/company_tickers.json"
        sec_response = requests.get(sec_url, headers=HEADERS)

        if sec_response.status_code == 200:
            sec_registry = sec_response.json()
            portfolio_seed = []

            for _, item in sec_registry.items():
                ticker = item['ticker'].upper().replace('.', '-')
                if ticker in all_unique_tickers:
                    portfolio_seed.append((ticker, item['title'], str(item['cik_str']).zfill(10)))

            cursor.executemany("""
                            INSERT OR IGNORE INTO assets (ticker, name, cik) VALUES (?, ?, ?);
                            """, portfolio_seed)
    
            conn.commit()
            print("Mapping relational connections between assets and market indices...")
            for index, tickers in index_maps.items():
                for t in tickers:
                    cursor.execute("SELECT id FROM assets WHERE ticker = ?;", (t,))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute("INSERT OR IGNORE INTO asset_index_mapping (asset_id, index_code) VALUES (?, ?);", (row[0], index))

            conn.commit()
            print("System setup complete! All index tracks mapped successfully.")

    except Exception as e:
        print(f"❌ Critical system connection breakdown: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()