import { moments, type Moment } from './moments';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

/** Fetch curated moments from the Python backend. Fall back to bundled editorial data for preview deployments. */
export async function fetchMoments(): Promise<Moment[]> {
  if (!API_URL) return moments;
  try {
    const response = await fetch(`${API_URL.replace(/\/$/, '')}/api/moments`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`API responded ${response.status}`);
    const data: unknown = await response.json();
    if (!Array.isArray(data)) throw new Error('Unexpected API response');
    return data as Moment[];
  } catch (error) {
    console.error('Hypeframe API unavailable; using preview catalog', error);
    return moments;
  }
}
