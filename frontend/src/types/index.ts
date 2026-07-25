/**
 * This file, index.ts, acts as the central type definition layer for the application. 
 * By defining strict TypeScript interfaces, I establish a robust contract between my 
 * frontend Vue app and my FastAPI backend. This prevents runtime data bugs, ensures auto-complete 
 * tooling works perfectly in my IDE, and cleanly documents the expected shape of my data.
 */

/**
 * The Asset interface defines the core metadata structure for a specific corporate entity.
 * This represents the structural footprint of a stock or public equity in my database.
 */

export interface Asset {
    id: number;
    ticker: string;
    name: string;
    cik: string;
    created_at?: string;
}

/**
 * The AssetFundamentals interface models the historical financial analytics matrix.
 * It is structured to absorb raw numeric sequences from corporate accounting packages.
 */
export interface AssetFundamentals {
    fiscal_year: number;
    revenue: number | null;
    operating_income: number | null;
    operating_margin: number | null;
    revenue_growth: number | null;
}