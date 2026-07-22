import { useState, useEffect } from "react";    
import type { FundamentalMetric} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export function useFundamentals(assetId: number | null) {
    const [fundamentals, setFundamentals] = useState<FundamentalMetric[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (assetId == null) {
            setFundamentals([]);
            return;
        }

        async function fetchFundamentals() {
            try {
                setLoading(true);
                const response = await fetch(`${API_BASE_URL}/fundamentals/${assetId}`);

                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error('No historical SEC metrics available for this asset.');
                    }
                    throw new Error(`Server connection error: ${response.status}`);
                }

                const data: FundamentalMetric[] = await response.json();
                setFundamentals(data);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to parse metric timeline');
                setFundamentals([]);
            } finally {
                setLoading(false);
            }
        }
        fetchFundamentals();
    }, [assetId]);

    return { fundamentals, loading, error };
}