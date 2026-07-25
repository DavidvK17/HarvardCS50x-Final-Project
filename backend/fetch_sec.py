"""
This script, fetch_sec.py, serves as the heavy-duty financial data extraction engine of my application. 
Its primary purpose is to systematically iterate through every asset stored in my database, query the U.S. Securities 
and Exchange Commission (SEC) EDGAR system using its unique Central Index Key (CIK), and download its complete 
XBRL financial history payload. It then implements parsing logic to sift through dense, multi-tiered JSON tags 
to extract historical annual revenue and operating income, weed out reporting anomalies using time-duration filters, 
dynamically compute mathematical metrics like operating margins and year-over-year revenue growth rates, and permanently 
commit this normalized corporate data matrix into the fundamentals table of my database.
"""

import sqlite3
import time
import requests

# From the built-in datetime module, import the datetime class so I can parse text timestamps 
# into calendar date objects for mathematical time calculations.
from datetime import datetime

DB_NAME = "portfolio.db"
HEADERS = {"User-Agent": "David Singer david.sing7@gmail.com"}

def fetch_company_facts(cik):
    """
    Programmatically hits the SEC EDGAR API endpoint to retrieve the full XBRL 
    corporate financial history payload for a specific corporation.
    """
    # The SEC database demands that all CIK identification numbers be exactly 10 characters long.
    # If a company CIK is shorter, I use .zfill(10) to prepend leading zeros (e.g., 320193 becomes "0000320193").
    padded_cik = str(cik).zfill(10)

    # Construct the precise API URL string targeting the specific company facts JSON repository.
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"

    try:
        # Dispatch the HTTP GET request to the SEC server, passing my required identity headers.
        response = requests.get(url, headers=HEADERS)

        # Check if the server responds with an HTTP status code of 200, which signifies an absolute success.
        if response.status_code == 200:
            # Parse the raw network response string directly into a native Python dictionary structure and return it.
            return response.json()
        else:
            # If the server responds with a failure code (like 403 Forbidden or 404 Not Found), log it and return None.
            print(f" ⚠️ Failed CIK{padded_cik}: HTTP {response.status_code}")
            return None
    except Exception as e:
        # If a networking anomaly or timeout occurs, intercept the crash gracefully and report it.
        print(f"Network error for CIK {padded_cik}: {e}")
        return None

def get_duration_days(start_str, end_str):
    """
    Calculates the exact number of calendar days elapsed between two date strings. 
    This acts as a structural validation filter for reporting periods.
    """
    # Defensive check: if either string parameter is missing or empty, return 0 immediately.
    if not start_str or not end_str:
        return 0
    try:
        # Use strptime to parse the ISO-formatted date strings ("YYYY-MM-DD") into comparative datetime objects.
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        # Subtract the two datetime objects to generate a timedelta object, then extract the raw integer day count.
        return (end_date - start_date).days
    except (ValueError, TypeError):
        # If formatting errors are encountered, fail safely by returning 0.
        return 0
    
def extract_annual_fundamentals(facts_json):
    """
    Parses the multi-tiered raw SEC JSON data package to isolate and extract clean 
    historical annual revenue and operating income metrics across fiscal years.
    """
    # Check if the incoming payload is empty or missing the core 'facts' dictionary block. 
    # If it is malformed, abort execution and return an empty dictionary.
    if not facts_json or 'facts' not in facts_json:
        return {}

    # Traverse the JSON structure to access the 'us-gaap' node, which houses accounting entries 
    # recognized under standard U.S. Generally Accepted Accounting Principles. Default to empty if missing.
    us_gaap = facts_json['facts'].get('us-gaap', {})

    # Design choice: Companies disclose revenue under varied accounting terms based on their sector. 
    # I define an array of alternative SEC taxonomy strings prioritized by common usage.
    revenue_tags = [
        'Revenues', 
        'RevenueFromContractWithCustomerExcludingAssessedTax', 
        'SalesRevenueNet', 
        'SalesRevenueGoodsNet',
        'RevenuesNetOfInterestExpense'
    ] 

    # Define alternative taxonomy tags utilized by corporations to report operational earnings.
    operating_inc_tags = [
        'OperatingIncomeLoss', 
        'OperatingProfitLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxes',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterestTax'
        ]

    # Initialize an in-memory storage dictionary to hold intermediate results mapped by fiscal year.
    yearly_records = {}

    def parse_metric(tags, metric_key):
        """
        Inner helper function that iterates through a set of alternative GAAP tags, 
        applies filtering logic, and extracts the target numerical values.
        """
        for tag in tags:
            # If the current taxonomy tag exists within the company's US GAAP filing history:
            if tag in us_gaap:
                units = us_gaap[tag].get('units', {})
                # Financial values are usually grouped by monetary unit. Attempt to pull the U.S. Dollar entries.
                usd_entries = units.get('USD', [])

                # Edge case: If the 'USD' array is missing but alternative unit arrays exist, 
                # extract the first available unit mapping to avoid losing data.
                if not usd_entries and units:
                    usd_entries = next(iter(units.values()))

                # Loop through every individual data node inside this metric's historical array.
                for entry in usd_entries:
                    # Crucial Filter: I am building a long-term fundamental chart, so I must strictly isolate 
                    # annual filings ('10-K' or amendments '10-K/A') and verify the fiscal period is full-year ('FY').
                    # This prevents intermediate quarterly results (10-Q) from corrupting my annual timeline.
                    if entry.get('form') in ['10-K', '10-K/A'] and entry.get('fp') == 'FY':
                        start = entry.get('start')
                        end = entry.get('end')

                        # Data Verification: Ensure the time span of this entry represents a full calendar year.
                        # Standard reporting periods can fluctuate slightly, so I enforce a strict window between 
                        # 330 and 400 days. If the entry spans only 90 days, it is a quarterly value wrapped in error, and I skip it.
                        if start and end:
                            days = get_duration_days(start, end)
                            if not (330 <= days <= 400):
                                continue

                        # Extract the target fiscal year, the absolute numeric balance value, and the filing submission date.
                        fy = entry.get('fy')
                        val = entry.get('val')
                        filed_date = entry.get('filed', '')

                        # Verify both variables contain non-null, valid numerical information.
                        if fy and val is not None:
                            try:
                                # Explicitly convert the fiscal year parameter into an integer.
                                fy = int(fy)
                            except ValueError:
                                continue

                            # If this year node has not been discovered yet, seed it with a baseline tracking dictionary structure.
                            if fy not in yearly_records:
                                yearly_records[fy] = {
                                    'revenue': None,
                                    'operating_income': None,
                                    '_rev_filed': '',
                                    '_op_filed': ''
                                }

                            # If processing a revenue metric:
                            if metric_key == 'revenue':
                                # Design Pattern (Handling Amendments): If this is my first time seeing data for this year, 
                                # OR if this specific filing date is newer than the one previously processed, overwrite 
                                # the slot. This guarantees that restated or corrected financials override old data.
                                if yearly_records[fy]['revenue'] is None or filed_date >= yearly_records[fy]['_rev_filed']:
                                    yearly_records[fy]['revenue'] = float(val)
                                    yearly_records[fy]['_rev_filed'] = filed_date

                            # If processing an operating income metric:
                            elif metric_key == 'operating_income':
                                # Apply the identical timestamp-recency override check for operating income data points.
                                if yearly_records[fy]['operating_income'] is None or filed_date >= yearly_records[fy]['_op_filed']:
                                    yearly_records[fy]['operating_income'] = float(val)
                                    yearly_records[fy]['_op_filed'] = filed_date

    # Execute the metric parser twice: once for revenue tags, once for operational profits.
    parse_metric(revenue_tags, 'revenue')
    parse_metric(operating_inc_tags, 'operating_income')

    # Construct a clean output buffer stripped of internal metadata filing tracking flags.
    clean_yearly_data = {}
    for year, data in yearly_records.items():
        clean_yearly_data[year] = {
            'revenue': data['revenue'],
            'operating_income': data['operating_income']
        }

    return clean_yearly_data

def run_pipeline():
    """
    The master operational workflow wrapper. Orchestrates database reads, loops over 
    tracked entities, processes calculations, and writes finalized metrics back to disk.
    """
    # Open a dedicated file transaction handle to my local SQLite architecture.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Query the assets table to harvest the internal unique ID, stock ticker symbol, 
    # and SEC CIK codes for every registered asset.
    cursor.execute("SELECT id, ticker, cik FROM assets WHERE cik IS NOT NULL;")
    stocks = cursor.fetchall()

    print(f"Starting ingestion pipeline for {len(stocks)} corporate equities...")

    # Iterate sequentially through my structural list of tracked stocks.
    for asset_id, ticker, cik in stocks:
        print(f"Processing {ticker} (CIK: {cik})...")

        # Programmatically hit the remote API endpoint to bring down the raw corporate facts payload.
        raw_facts = fetch_company_facts(cik)
        if not raw_facts:
            # If the retrieval fails (e.g., network timeout or invalid CIK), skip to the next stock.
            continue

        # Extract the fundamental accounting blocks from the raw data.
        financials = extract_annual_fundamentals(raw_facts)

        # Sort the years chronologically so I can perform sequential year-over-year mathematical logic.
        sorted_years = sorted(financials.keys())

        # Enumerate through the sorted years vector to analyze each financial year's metrics.
        for i, year in enumerate(sorted_years):
            metrics = financials[year]
            rev = metrics['revenue']
            op_inc = metrics['operating_income']

            # Optimization Check: If both metrics return empty, this calendar block is devoid of value. Skip it.
            if rev is None and op_inc is None:
                continue # Skip dead empty years

            # Calculate operational efficiency margins as a percentage value. 
            # Formula: (Operating Income / Revenue) * 100. Guard against division by zero.
            margin = (op_inc / rev * 100) if rev and op_inc is not None else None

            # Initialize my year-over-year growth calculation variable as None.
            growth = None

            # If we are past index 0, a historical comparison baseline year exists in our array.
            if i > 0:
                prev_year = sorted_years[i-1]

                # Check for strict continuity: Ensure the previous entry is exactly 1 calendar year prior. 
                # This prevents artificial growth spikes if a company missed filing data for a gap year.
                if year - prev_year == 1:
                    prev_rev = financials[prev_year]['revenue']

                    # Formula: ((Current Revenue - Previous Revenue) / Previous Revenue) * 100
                    if rev and prev_rev:
                        growth = ((rev - prev_rev) / prev_rev) * 100

            # Commit the calculated fundamental matrix back to the localized SQL table structure.
            # I use 'INSERT OR REPLACE' because if a year entry already exists, I want to refresh it 
            # with the newest computed margins or growth calculations derived from the latest scraped files.
            cursor.execute("""
                        INSERT OR REPLACE INTO fundamentals
                        (asset_id, fiscal_year, revenue, operating_income, operating_margin, revenue_growth)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """, (asset_id, year, rev, op_inc, margin, growth))
        
        print(f"Successfully mapped and stored data for {ticker}.")

        # Guardrail: The SEC explicitly restricts third-party scrapers to a maximum speed of 
        # 10 network requests per second. Implementing an explicit sleep pause of 0.15 seconds 
        # throttles my pipeline safely to roughly 6.6 requests per second, completely preventing my IP address 
        # from being blacklisted by their network firewalls.
        time.sleep(0.15)

    # Save the transactional block permanently to disk and safely close out the database file descriptor handles.
    conn.commit()
    conn.close()
    print("\n Fundamental data matrix generation complete!")

# Runtime Verification: Triggers the master pipeline function if the terminal executes 
# this individual script file explicitly.
if __name__ == "__main__":
    run_pipeline()