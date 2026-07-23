import sqlite3
import time
import requests
from datetime import datetime

DB_NAME = "portfolio.db"
HEADERS = {"User-Agent": "David Singer david.sing7@gmail.com"}

def fetch_company_facts(cik):
    """Retrieves the full XBRL corporate financial history data pacakge from SEC EDGAR. """
    padded_cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f" ⚠️ Failed CIK{padded_cik}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Network error for CIK {padded_cik}: {e}")
        return None

def get_duration_days(start_str, end_str):
    if not start_str or not end_str:
        return 0
    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        return (end_date - start_date).days
    except (ValueError, TypeError):
        return 0
    
def extract_annual_fundamentals(facts_json):
    """Parse raw JSON facts to map revenue and operating income across fiscal years """
    if not facts_json or 'facts' not in facts_json:
        return {}
    
    us_gaap = facts_json['facts'].get('us-gaap', {})
    revenue_tags = [
        'Revenues', 
        'RevenueFromContractWithCustomerExcludingAssessedTax', 
        'SalesRevenueNet', 
        'SalesRevenueGoodsNet',
        'RevenuesNetOfInterestExpense'
    ] 
    operating_inc_tags = [
        'OperatingIncomeLoss', 
        'OperatingProfitLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxes',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterestTax'
        ]
    
    yearly_records = {}

    def parse_metric(tags, metric_key):
        for tag in tags:
            if tag in us_gaap:
                units = us_gaap[tag].get('units', {})
                usd_entries = units.get('USD', [])

                if not usd_entries and units:
                    usd_entries = next(iter(units.values()))
                
                for entry in usd_entries:
                    if entry.get('form') in ['10-K', '10-K/A'] and entry.get('fp') == 'FY':
                        start = entry.get('start')
                        end = entry.get('end')
                        if start and end:
                            days = get_duration_days(start, end)
                            if not (330 <= days <= 400):
                                continue

                        fy = entry.get('fy')
                        val = entry.get('val')
                        filed_date = entry.get('filed', '')

                        if fy and val is not None:
                            try:
                                fy = int(fy)
                            except ValueError:
                                continue

                            if fy not in yearly_records:
                                yearly_records[fy] = {
                                    'revenue': None,
                                    'operating_income': None,
                                    '_rev_filed': '',
                                    '_op_filed': ''
                                }

                            if metric_key == 'revenue':
                                if yearly_records[fy]['revenue'] is None or filed_date >= yearly_records[fy]['_rev_filed']:
                                    yearly_records[fy]['revenue'] = float(val)
                                    yearly_records[fy]['_rev_filed'] = filed_date
                            
                            elif metric_key == 'operating_income':
                                if yearly_records[fy]['operating_income'] is None or filed_date >= yearly_records[fy]['_op_filed']:
                                    yearly_records[fy]['operating_income'] = float(val)
                                    yearly_records[fy]['_op_filed'] = filed_date
    
    parse_metric(revenue_tags, 'revenue')
    parse_metric(operating_inc_tags, 'operating_income')

    clean_yearly_data = {}
    for year, data in yearly_records.items():
        clean_yearly_data[year] = {
            'revenue': data['revenue'],
            'operating_income': data['operating_income']
        }

    return clean_yearly_data

def run_pipeline():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, ticker, cik FROM assets WHERE cik IS NOT NULL;")
    stocks = cursor.fetchall()

    print(f"Starting ingestion pipeline for {len(stocks)} corporate equities...")

    for asset_id, ticker, cik in stocks:
        print(f"Processing {ticker} (CIK: {cik})...")

        raw_facts = fetch_company_facts(cik)
        if not raw_facts:
            continue

        financials = extract_annual_fundamentals(raw_facts)
        sorted_years = sorted(financials.keys())

        for i, year in enumerate(sorted_years):
            metrics = financials[year]
            rev = metrics['revenue']
            op_inc = metrics['operating_income']

            if rev is None and op_inc is None:
                continue # Skip dead empty years

            # compute operational efficiency margins
            margin = (op_inc / rev * 100) if rev and op_inc is not None else None

            growth = None
            if i > 0:
                prev_year = sorted_years[i-1]
                if year - prev_year == 1:
                    prev_rev = financials[prev_year]['revenue']
                    if rev and prev_rev:
                        growth = ((rev - prev_rev) / prev_rev) * 100
            
            cursor.execute("""
                        INSERT OR REPLACE INTO fundamentals
                        (asset_id, fiscal_year, revenue, operating_income, operating_margin, revenue_growth)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """, (asset_id, year, rev, op_inc, margin, growth))
        
        print(f"Successfully mapped and stored data for {ticker}.")

        # Respect SEC rate limits (Max 10 requests per second allowed safely)
        time.sleep(0.15)

    conn.commit()
    conn.close()
    print("\n Fundamental data matrix generation complete!")

if __name__ == "__main__":
    run_pipeline()