import sqlite3

DB_NAME = "portfolio.db"

def initialize_database():
    print(f"Creating database file: {DB_NAME}...")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Enable foreigh keys 
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Assets Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS assets (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   ticker TEXT UNIQUE NOT NULL,
                   name TEXT NOT NULL,
                   asset_type TEXT NOT NULL, -- 'STOCK' or 'ETF'
                   allocation_eur REAL NOT NULL,
                   cik TEXT UNIQUE, -- SEC CIK code (Null for ETFs)
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
    
    # Portfolio Positions:
    portfolio_seed = [
        ("ACWI", "SPDR MSCI ACWI IMI ETF Acc", "ETF", 3825.0, None),
        ("MSFT", "Microsoft", "STOCK", 1703.0, "0000789019"),
        ("BRK.B", "Berkshire Hathaway", "STOCK", 1700.0, "0001067983"),
        ("COST", "Costco", "STOCK", 1701.0, "0000909832"),
        ("GOOGL", "Google", "STOCK", 1275.0, "0001652044"),
        ("AMZN", "Amazon", "STOCK", 1275.0, "0001018724"),
        ("V", "Visa", "STOCK", 851.0, "0001403161"),
        ("SPGI", "S&P Global", "STOCK", 425.0, "0000064040"),
        ("AAPL", "Apple", "STOCK", 425.0, "0000320193"),
        ("LIN", "Linde", "STOCK", 426.0, "0001707925"),
    ]

    print("Seeding asset positions and Euro allocations...")
    cursor.executemany("""
                       INSERT OR IGNORE INTO assets (ticker, name, asset_type, allocation_eur, cik) VALUES (?, ?, ?, ?, ?);
                       """, portfolio_seed)
    
    conn.commit()
    conn.close()
    print("Databse successfully generated and seeded with 10 holdings!")

if __name__ == "__main__":
    initialize_database()