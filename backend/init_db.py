import sqlite3
import requests
import re

DB_NAME = "portfolio.db"
HEADERS = {"User-Agent": "David Singer david.sing7@gmail.com"}

# ====================================================================================
# CONFIGURATION MODULE: TOGGLE YOUR TARGET INDEX HERE!
# Options available: "DOW30" (30 Stocks), "NASDAQ100" (100 Stocks), "SP500" (500Stocks)
# ====================================================================================

INDEX_SELECTION = "SP500"

def get_index_tickers(index_type):
    print(f"Scanning current {index_type} components list via web registry...")

    if index_type == "SP500":
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    elif index_type == "NASDAQ100":
        url = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"
    elif index_type == "DOW30":
        url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    else:
        raise ValueError("Unsupported index selection type.")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to scan target index: HTTP {response.status_code}")
            return set()

        html = response.text

        if "id=\"constituents\"" in html:
            html = html.split("id=\"constituents\"")[1].split("</table>")[0]
        elif index_type == "DOW30":
            parts = html.split('class="wikitable"')
            for part in parts[1:]:
                if "Goldman Sachs" in part or "Microsoft" in part:
                    html = part.split('<table>')[0]
                    break

        raw_matches = re.findall(r'>([A-Z]{1,5}(?:\.[A-Z])?)<\/a>', html)

        exclude_set = {'NYSE', 'NASDAQ', 'CBOE', 'SEC', 'CIK', 'USD', 'DJIA', 'S', 'P', 'GICS', 'USA'}
        target_tickers = set()

        for ticker in raw_matches:
            clean_ticker = ticker.strip().replace('.', '-')
            if clean_ticker and clean_ticker not in exclude_set and not clean_ticker.isdigit():
                target_tickers.add(clean_ticker)

        print(f"Discovered {len(target_tickers)} unique symbols in registry mapping.")
        return target_tickers

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

    target_symbols = get_index_tickers(INDEX_SELECTION)

    if not target_symbols:
        print("Aborting database seed: No symbols were retrieved from the web registry.")
        conn.close()
        return
  
    print("Connecting to master SEC EDGAR global data vault maps...")
    try:
        sec_url = "https://www.sec.gov/files/company_tickers.json"
        sec_response = requests.get(sec_url, headers=HEADERS)

        if sec_response.status_code == 200:
            sec_registry = sec_response.json()
            portfolio_seed = []

            for _, item in sec_registry.items():
                ticker = item['ticker'].upper().replace('.', '-')
                name = item['title']
                cik = str(item['cik_str']).zfill(10)

                if ticker in target_symbols:
                    portfolio_seed.append((ticker, name, cik))

            print(f" Seeding SQL engine database tables with validated entries ({len(portfolio_seed)} units matching)...")  
            cursor.executemany("""
                            INSERT OR IGNORE INTO assets (ticker, name, cik) VALUES (?, ?, ?);
                            """, portfolio_seed)
    
            conn.commit()
            print(f"Database initialization complete! Target set successfully configured to: {INDEX_SELECTION}")
        else:
            print(f"Failed to sync with SEC master directories: HTTP {sec_response.status_code}")

    except Exception as e:
        print(f"❌ Critical system connection breakdown: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()