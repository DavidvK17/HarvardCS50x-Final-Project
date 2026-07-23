export interface Asset {
    id: number;
    ticker: string;
    name: string;
    cik: string;
    created_at?: string;
}

export interface AssetFundamentals {
    fiscal_year: number;
    revenue: number | null;
    operating_income: number | null;
    operating_margin: number | null;
    revenue_growth: number | null;
}