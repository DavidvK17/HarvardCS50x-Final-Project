import sqlite3

DB_NAME = "portfolio.db"

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
    
    # Portfolio Positions:
    portfolio_seed = [
        ("MSFT", "Microsoft", "0000789019"),
        ("COST", "Costco", "0000909832"),
        ("GOOGL", "Google", "0001652044"),
        ("AMZN", "Amazon", "0001018724"),
        ("V", "Visa", "0001403161"),
        ("SPGI", "S&P Global", "0000064040"),
        ("AAPL", "Apple", "0000320193"),
        ("LIN", "Linde", "0001707925"),
    ]

    print("Seeding asset positions and Euro allocations...")
    cursor.executemany("""
                       INSERT OR IGNORE INTO assets (ticker, name, cik) VALUES (?, ?, ?);
                       """, portfolio_seed)
    
    conn.commit()
    conn.close()
    print("Databse successfully generated and seeded with all 8 holdings!")

if __name__ == "__main__":
    initialize_database()