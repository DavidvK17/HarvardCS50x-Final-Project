import { useState, useEffect } from "react";
import type { Asset } from '../types'

const API_BASE_URL = "http://127.0.0.1:8000/api";

export function useAssets() {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchAssets() {
            try {
                setLoading(true);
                const response = await fetch(`${API_BASE_URL}/assets`);

                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }

                const data: Asset[] = await response.json();
                setAssets(data);
                setError(null);
            } catch(err) {
                setError(err instanceof Error ? err.message : 'An unknown network error occurred');
            } finally {
                setLoading(false);
            }
        }
        fetchAssets();
    }, []);

    return { assets, loading, error};
}


