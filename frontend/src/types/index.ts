export interface Asset {
    id: number;
    ticker: string;
    name: string;
    asset_type: 'STOCK' | "ETF";
    allocation_eur: number;
    cik: string | null;
}

export interface FundamentalMetric {
    fiscal_year: number;
    revenue: number | null;
    operating_income: number | null;
    operating_margin: number | null;
    revenue_growth: number | null;
}

export interface SelectionState {
    primaryAssetId: number | null;
    compareAssetId: number | null;
}